from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from app.assets.models import AssetManifest
from app.captions.align import FasterWhisperTranscriber, align_narration
from app.editorial.ollama import OllamaJsonClient
from app.rendering.package import build_render_package
from app.rendering.runner import RemotionRunner
from app.shorts.pipeline import build_short_story
from app.visuals.thumbnail_v2 import render_thumbnail_variants


@dataclass(frozen=True)
class ProductionOutputs:
    long_video: Path
    short_video: Path | None
    thumbnails: tuple[Path, ...]
    render_package: Path
    short_render_package: Path | None = None
    short_error: str | None = None
    audio: Path | None = None


def renderer_mode(value: str | None = None) -> str:
    selected = (value or os.getenv("AUTOTUBE_RENDERER", "legacy")).strip().lower()
    if selected not in {"legacy", "professional"}:
        raise ValueError("AUTOTUBE_RENDERER must be 'legacy' or 'professional'")
    return selected


def composition_id(channel_id: str, format_name: str) -> str:
    channel = channel_id.strip().lower()
    if channel not in {"kernelrush", "lobbysignal"}:
        raise ValueError(f"unsupported channel for renderer: {channel_id}")
    if format_name not in {"long", "short"}:
        raise ValueError(f"unsupported renderer format: {format_name}")
    prefix = "KernelRush" if channel == "kernelrush" else "LobbySignal"
    suffix = "Long" if format_name == "long" else "Short"
    return prefix + suffix


def render_professional_episode(
    *,
    channel_cfg: dict,
    title: str,
    script: str,
    scene_plan,
    packet: dict,
    asset_manifest: AssetManifest,
    tts,
    out_dir: Path,
    llm=None,
    runner=None,
    transcriber=None,
    caption_aligner=align_narration,
    package_builder=build_render_package,
    thumbnail_renderer=render_thumbnail_variants,
    short_builder=build_short_story,
) -> ProductionOutputs:
    output = Path(out_dir)
    output.mkdir(parents=True, exist_ok=True)
    channel_id = str(channel_cfg.get("id", scene_plan.channel_id))

    render_runner = runner or RemotionRunner()
    speech_transcriber = transcriber or FasterWhisperTranscriber()

    narration = Path(tts.synthesize(script, output / "narration.wav"))
    captions = caption_aligner(narration, script, speech_transcriber)
    long_package = package_builder(
        channel_cfg,
        title,
        script,
        scene_plan,
        captions,
        asset_manifest,
        narration,
        output / "render-package-long",
        format="long",
    )
    long_video = render_runner.render(
        long_package,
        composition_id(channel_id, "long"),
        output / "video.mp4",
    )
    thumbnails = tuple(
        thumbnail_renderer(
            channel_cfg,
            title,
            scene_plan,
            asset_manifest,
            output / "thumbnails",
            count=5,
        )
    )

    short_video: Path | None = None
    short_package: Path | None = None
    short_error: str | None = None
    try:
        short_llm = llm or OllamaJsonClient()
        short_story = short_builder(channel_id, packet, script, short_llm)
        short_audio = Path(tts.synthesize(short_story.script, output / "short-narration.wav"))
        short_captions = caption_aligner(short_audio, short_story.script, speech_transcriber)
        short_package = package_builder(
            channel_cfg,
            title,
            short_story.script,
            short_story.scene_plan,
            short_captions,
            asset_manifest,
            short_audio,
            output / "render-package-short",
            format="short",
        )
        short_video = render_runner.render(
            short_package,
            composition_id(channel_id, "short"),
            output / "short.mp4",
        )
    except Exception as exc:  # noqa: BLE001 - optional Short failure must not invalidate long-form
        short_error = str(exc)
        short_video = None
        short_package = None

    return ProductionOutputs(
        long_video=Path(long_video),
        short_video=Path(short_video) if short_video else None,
        thumbnails=thumbnails,
        render_package=Path(long_package),
        short_render_package=Path(short_package) if short_package else None,
        short_error=short_error,
        audio=narration,
    )
