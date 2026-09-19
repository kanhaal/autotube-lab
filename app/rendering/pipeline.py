from __future__ import annotations

import inspect
import os
from dataclasses import dataclass
from pathlib import Path

from app.assets.models import AssetManifest
from app.assets.service import prepare_assets
from app.audio.library import AudioLibrary
from app.audio.mix import mix_episode_audio
from app.audio.sound_design import build_lowpass_windows, build_sound_design_events, needs_sound_design
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


def _configured_audio_library() -> AudioLibrary:
    path = Path(os.getenv("AUTOTUBE_AUDIO_LIBRARY", "config/audio/library.yml"))
    if not path.is_file():
        return AudioLibrary(())
    return AudioLibrary.from_yaml(path)


def _release(resource) -> None:
    release = getattr(resource, "release", None)
    if callable(release):
        release()


def _master_audio(
    narration: Path,
    channel_cfg: dict,
    out: Path,
    *,
    scene_plan=None,
    duration_seconds: float | None = None,
) -> Path:
    audio_cfg = channel_cfg.get("audio") or {}
    if not isinstance(audio_cfg, dict):
        audio_cfg = {}
    channel_id = str(channel_cfg.get("id", "")).strip().lower()
    mood = str(audio_cfg.get("mood", "")).strip()
    music = None
    if bool(audio_cfg.get("music_enabled", False)):
        selected = _configured_audio_library().select("music", channel_id, mood)
        if selected is not None:
            music = selected.path

    events = ()
    lowpass_windows = ()
    if scene_plan is not None and needs_sound_design(scene_plan):
        duration = duration_seconds
        if duration is None or duration <= 0:
            try:
                from app.rendering.ffmpeg import probe_media

                duration = probe_media(Path(narration)).format_duration
            except Exception:  # noqa: BLE001 - sound design enrichment must not break valid mastering
                duration = None
        if duration is not None and duration > 0:
            events = build_sound_design_events(
                scene_plan,
                duration_seconds=duration,
                out_dir=Path(out).parent / "sound-design",
                channel_id=channel_id,
            )
            lowpass_windows = build_lowpass_windows(
                scene_plan,
                duration_seconds=duration,
            )
    return Path(
        mix_episode_audio(
            Path(narration),
            music,
            events,
            Path(out),
            lowpass_windows=lowpass_windows,
        )
    )


def _caption_duration(captions) -> float | None:
    ends = [
        float(getattr(cue, "end", 0.0) or 0.0)
        for cue in (captions or ())
        if float(getattr(cue, "end", 0.0) or 0.0) > 0
    ]
    return max(ends) if ends else None


def _invoke_master_audio(master, narration: Path, channel_cfg: dict, out: Path, *, scene_plan, captions):
    kwargs = {}
    try:
        parameters = inspect.signature(master).parameters.values()
        names = {parameter.name for parameter in parameters}
        accepts_kwargs = any(parameter.kind is inspect.Parameter.VAR_KEYWORD for parameter in parameters)
    except (TypeError, ValueError):
        names = set()
        accepts_kwargs = False
    if accepts_kwargs or "scene_plan" in names:
        kwargs["scene_plan"] = scene_plan
    if accepts_kwargs or "duration_seconds" in names:
        kwargs["duration_seconds"] = _caption_duration(captions)
    return Path(master(narration, channel_cfg, out, **kwargs))


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
    asset_preparer=prepare_assets,
) -> ProductionOutputs:
    output = Path(out_dir)
    output.mkdir(parents=True, exist_ok=True)
    channel_id = str(channel_cfg.get("id", scene_plan.channel_id))

    render_runner = runner or RemotionRunner()
    speech_transcriber = transcriber or FasterWhisperTranscriber()

    try:
        narration = Path(tts.synthesize(script, output / "narration.wav"))
    finally:
        _release(tts)
    try:
        captions = caption_aligner(narration, script, speech_transcriber)
    finally:
        _release(speech_transcriber)
    master_audio = _invoke_master_audio(
        _master_audio,
        narration,
        channel_cfg,
        output / "master.wav",
        scene_plan=scene_plan,
        captions=captions,
    )
    long_package = package_builder(
        channel_cfg,
        title,
        script,
        scene_plan,
        captions,
        asset_manifest,
        master_audio,
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
        owned_short_llm = llm is None
        short_llm = llm or OllamaJsonClient()
        try:
            short_story = short_builder(channel_id, packet, script, short_llm)
        finally:
            if owned_short_llm:
                unload = getattr(short_llm, "unload", None)
                if callable(unload):
                    unload()
        short_assets = asset_preparer(
            short_story.scene_plan,
            packet,
            channel_cfg,
            output / "short-assets",
        )
        try:
            short_audio = Path(tts.synthesize(short_story.script, output / "short-narration.wav"))
        finally:
            _release(tts)
        try:
            short_captions = caption_aligner(short_audio, short_story.script, speech_transcriber)
        finally:
            _release(speech_transcriber)
        short_master_audio = _invoke_master_audio(
            _master_audio,
            short_audio,
            channel_cfg,
            output / "short-master.wav",
            scene_plan=short_story.scene_plan,
            captions=short_captions,
        )
        short_package = package_builder(
            channel_cfg,
            title,
            short_story.script,
            short_story.scene_plan,
            short_captions,
            short_assets,
            short_master_audio,
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
        audio=master_audio,
    )
