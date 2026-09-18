from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from app.assets.models import AssetManifest, AssetRecord
from app.audio.mix import SfxEvent, mix_episode_audio
from app.audio.sound_design import build_lowpass_windows, build_sound_design_events
from app.captions.align import FasterWhisperTranscriber, align_narration
from app.config import channel_config
from app.narration.backend import ConfiguredTTS, select_tts_backend
from app.narration.fallback import FallbackTTS
from app.planning.scene_schema import parse_scene_plan
from app.rendering.ffmpeg import probe_media
from app.rendering.history import create_render_run
from app.rendering.package import build_render_package
from app.rendering.pipeline import composition_id
from app.rendering.runner import RemotionRunner
from app.visuals.thumbnail_v2 import render_thumbnail_variants


def _font(size: int, bold: bool = False):
    candidates = [
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
        Path(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
            if bold
            else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        ),
    ]
    for path in candidates:
        if path.is_file():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def _render_local_card(story: dict, out: Path, channel_cfg: dict, *, fallback: bool = False) -> Path:
    brand = channel_cfg.get("brand") or {}
    background = brand.get("background", "#080B12")
    foreground = brand.get("foreground", "#F7FAFF")
    accent = brand.get("accent", "#66F2C1")
    image = Image.new("RGB", (1440, 900), background)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((70, 65, 1370, 835), radius=42, outline=accent, width=6)
    draw.text(
        (115, 115),
        "SAFE EDITORIAL FALLBACK" if fallback else story["source_visual"]["label"],
        fill=accent,
        font=_font(48, bold=True),
    )
    body = (
        "Synthetic fixture. No source image was available or required."
        if fallback
        else story["source_visual"]["body"]
    )
    words = body.split()
    lines: list[str] = []
    current = ""
    for word in words:
        proposed = f"{current} {word}".strip()
        if draw.textbbox((0, 0), proposed, font=_font(42))[2] > 1160 and current:
            lines.append(current)
            current = word
        else:
            current = proposed
    if current:
        lines.append(current)
    for index, line in enumerate(lines[:6]):
        draw.text((115, 260 + index * 62), line, fill=foreground, font=_font(42))
    draw.text(
        (115, 730),
        f"{channel_cfg.get('name', story['channel_id'])} · LOCAL SAMPLE",
        fill=foreground,
        font=_font(30, bold=True),
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    image.save(out, format="PNG", optimize=True)
    return out


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _tts(channel_cfg: dict) -> ConfiguredTTS:
    voice = channel_cfg.get("voice") or {}
    profile = voice.get("profile", "default")
    primary_name = os.getenv(
        "AUTOTUBE_TTS_BACKEND",
        voice.get("backend", "chatterbox"),
    ).strip().lower()
    primary = select_tts_backend(
        primary_name,
        voice_profiles={profile: voice.get("settings", {})},
    )
    fallback = select_tts_backend(
        voice.get("fallback_backend", "kokoro"),
        voice_profiles={profile: voice.get("fallback_settings", {})},
    )
    return ConfiguredTTS(FallbackTTS(primary, fallback), profile)


def _generate_audio_fixture(root: Path) -> tuple[Path, Path]:
    music = root / "synthetic-music.wav"
    sfx = root / "synthetic-sfx.wav"
    root.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=92:sample_rate=48000:duration=90",
            "-af",
            "volume=0.08",
            str(music),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=880:sample_rate=48000:duration=0.16",
            "-af",
            "afade=t=out:st=0.05:d=0.11,volume=0.25",
            str(sfx),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return music, sfx


def _scene_plan(story: dict, format_name: str):
    return parse_scene_plan(
        {
            "channel_id": story["channel_id"],
            "format": "longform" if format_name == "long" else "short",
            "scenes": story[format_name]["scenes"],
        }
    )


def _assets(story: dict, plan, source_card: Path, fallback_card: Path) -> AssetManifest:
    source_scene = next(scene for scene in plan.scenes if scene.scene_type == "source_browser")
    fallback_scene = next(scene for scene in plan.scenes if scene.scene_type == "fallback_editorial")
    captured_at = datetime.now(timezone.utc)
    return AssetManifest(
        records=(
            AssetRecord(
                id="source-card",
                kind="source_screenshot",
                local_path=str(source_card),
                source_url=None,
                source_name="synthetic local fixture",
                usage="evidence",
                license_note="generated locally for AutoTube sample QA",
                sha256=_sha256(source_card),
                captured_at=captured_at,
                scene_id=source_scene.id,
            ),
            AssetRecord(
                id="fallback-card",
                kind="fallback_editorial",
                local_path=str(fallback_card),
                source_url=None,
                source_name=None,
                usage="fallback",
                license_note="generated locally for AutoTube sample QA",
                sha256=_sha256(fallback_card),
                captured_at=captured_at,
                scene_id=fallback_scene.id,
            ),
        )
    )


def _script(plan) -> str:
    return " ".join(scene.narration for scene in plan.scenes)


def render_story(fixture: Path, output_root: Path) -> dict:
    story = json.loads(Path(fixture).read_text(encoding="utf-8"))
    channel_id = story["channel_id"]
    channel_cfg = channel_config(channel_id)
    render_run = create_render_run(Path(output_root), channel_id)
    target = render_run.directory

    source_card = _render_local_card(story, target / "source-card.png", channel_cfg)
    fallback_card = _render_local_card(
        story,
        target / "fallback-card.png",
        channel_cfg,
        fallback=True,
    )
    music, sfx = _generate_audio_fixture(target / "audio-fixtures")
    runner = RemotionRunner()
    prepared: dict[str, dict] = {}

    for format_name in ("long", "short"):
        plan = _scene_plan(story, format_name)
        prepared[format_name] = {
            "plan": plan,
            "script": _script(plan),
            "assets": _assets(story, plan, source_card, fallback_card),
        }

    tts = _tts(channel_cfg)
    try:
        for format_name in ("long", "short"):
            item = prepared[format_name]
            item["narration"] = Path(
                tts.synthesize(item["script"], target / f"{format_name}-narration.wav")
            )
    finally:
        tts.release()

    transcriber = FasterWhisperTranscriber()
    try:
        for format_name in ("long", "short"):
            item = prepared[format_name]
            item["captions"] = align_narration(
                item["narration"],
                item["script"],
                transcriber,
            )
    finally:
        transcriber.release()

    rendered: dict[str, str | list[str]] = {
        "run_id": render_run.run_id,
        "run_dir": str(target.resolve()),
        "latest_pointer": str(render_run.latest_pointer.resolve()),
    }
    events = tuple(
        SfxEvent(path=sfx, start_ms=int(float(item["at"]) * 1000), volume=0.25)
        for item in story["audio"]["sfx_events"]
    )

    for format_name in ("long", "short"):
        item = prepared[format_name]
        duration = probe_media(item["narration"]).format_duration
        editorial_events = build_sound_design_events(
            item["plan"],
            duration_seconds=duration,
            out_dir=target / "sound-design",
            channel_id=channel_id,
        )
        lowpass_windows = build_lowpass_windows(
            item["plan"],
            duration_seconds=duration,
        )
        master = mix_episode_audio(
            item["narration"],
            music,
            tuple(events) + tuple(editorial_events),
            target / f"{format_name}-master.wav",
            lowpass_windows=lowpass_windows,
        )
        package = build_render_package(
            channel_cfg,
            story["title"],
            item["script"],
            item["plan"],
            item["captions"],
            item["assets"],
            master,
            target / f"render-package-{format_name}",
            format=format_name,
        )
        video = runner.render(
            package,
            composition_id(channel_id, format_name),
            target / ("long.mp4" if format_name == "long" else "short.mp4"),
        )
        rendered[format_name] = str(video)
        if format_name == "long":
            rendered["thumbnails"] = [
                str(path)
                for path in render_thumbnail_variants(
                    channel_cfg,
                    story["title"],
                    item["plan"],
                    item["assets"],
                    target / "thumbnails",
                    count=5,
                )
            ]

    (target / "sample-result.json").write_text(
        json.dumps(rendered, indent=2),
        encoding="utf-8",
    )
    return rendered


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("fixture", type=Path)
    parser.add_argument("--output", type=Path, default=Path("output/samples"))
    args = parser.parse_args()
    print(json.dumps(render_story(args.fixture, args.output), indent=2))


if __name__ == "__main__":
    main()
