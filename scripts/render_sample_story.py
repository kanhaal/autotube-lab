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
    secondary = brand.get("secondary", accent)
    image = Image.new("RGB", (1440, 900), background)
    draw = ImageDraw.Draw(image)

    if fallback:
        # A safe original editorial graphic, deliberately not a fake website/source screenshot.
        for x in range(0, 1440, 72):
            draw.line((x, 0, x, 900), fill="#141B25", width=1)
        for y in range(0, 900, 72):
            draw.line((0, y, 1440, y), fill="#141B25", width=1)
        draw.ellipse((870, -170, 1510, 470), outline=secondary, width=3)
        draw.ellipse((1010, -40, 1370, 320), outline=accent, width=7)
        draw.rounded_rectangle((105, 120, 780, 670), radius=52, fill="#0D131D", outline="#1E2937", width=2)
        draw.text((150, 165), "ORIGINAL EDITORIAL", fill=accent, font=_font(25, bold=True))
        draw.text((150, 250), "NO SOURCE", fill=foreground, font=_font(72, bold=True))
        draw.text((150, 335), "IMAGE NEEDED", fill=foreground, font=_font(72, bold=True))
        draw.rounded_rectangle((150, 480, 380, 530), radius=25, fill=accent)
        draw.text((178, 492), "SAFE FALLBACK", fill=background, font=_font(22, bold=True))
        draw.text(
            (150, 590),
            "Original motion graphics keep the edit moving.",
            fill="#A8B3C2",
            font=_font(25),
        )
        draw.line((900, 610, 1270, 610), fill=accent, width=5)
        draw.line((970, 660, 1330, 660), fill=secondary, width=3)
        draw.line((1040, 710, 1250, 710), fill="#334155", width=2)
    else:
        # Synthetic browser/dashboard fixture that behaves more like real source media.
        draw.rounded_rectangle((55, 45, 1385, 855), radius=28, fill="#0B1018", outline="#263244", width=2)
        draw.rounded_rectangle((55, 45, 1385, 122), radius=28, fill="#111925")
        draw.rectangle((55, 90, 1385, 122), fill="#111925")
        for index, color in enumerate(("#FF6B6B", "#FFD166", "#66F2C1")):
            draw.ellipse((86 + index * 34, 72, 104 + index * 34, 90), fill=color)
        draw.rounded_rectangle((220, 67, 870, 101), radius=17, fill="#080D14")
        draw.text((247, 73), "local://synthetic-benchmark/dashboard", fill="#75859A", font=_font(17))
        draw.text((1040, 70), "VERIFIED FIXTURE", fill=accent, font=_font(18, bold=True))

        draw.text((105, 165), story["source_visual"]["label"], fill=foreground, font=_font(48, bold=True))
        draw.text((105, 225), "Synthetic dashboard • acceptance-test source", fill="#8796AA", font=_font(22))

        body = story["source_visual"]["body"]
        words = body.split()
        lines: list[str] = []
        current = ""
        for word in words:
            proposed = f"{current} {word}".strip()
            if draw.textbbox((0, 0), proposed, font=_font(26))[2] > 580 and current:
                lines.append(current)
                current = word
            else:
                current = proposed
        if current:
            lines.append(current)
        for index, line in enumerate(lines[:4]):
            draw.text((105, 305 + index * 42), line, fill="#CBD5E1", font=_font(26))

        # Source-like metadata and state chips.
        chips = (("LOCAL", accent), ("SYNTHETIC", secondary), ("NO LIVE CLAIM", "#94A3B8"))
        chip_x = 105
        for label, color in chips:
            width = draw.textbbox((0, 0), label, font=_font(17, bold=True))[2] + 42
            draw.rounded_rectangle((chip_x, 505, chip_x + width, 545), radius=20, outline=color, width=2)
            draw.text((chip_x + 20, 516), label, fill=color, font=_font(17, bold=True))
            chip_x += width + 14

        # Dashboard metric cards.
        draw.rounded_rectangle((105, 610, 335, 760), radius=24, fill="#101925", outline="#223148", width=2)
        draw.text((132, 638), "BASELINE", fill="#7C8CA1", font=_font(18, bold=True))
        draw.text((132, 680), "42 ms", fill=foreground, font=_font(43, bold=True))
        draw.rounded_rectangle((360, 610, 590, 760), radius=24, fill="#101925", outline=accent, width=2)
        draw.text((387, 638), "TUNED", fill=accent, font=_font(18, bold=True))
        draw.text((387, 680), "18 ms", fill=accent, font=_font(43, bold=True))

        # Trend panel on the right.
        draw.rounded_rectangle((665, 165, 1325, 760), radius=30, fill="#0E1622", outline="#213047", width=2)
        draw.text((710, 205), "QUEUE LATENCY / TEST PASSES", fill="#91A1B5", font=_font(20, bold=True))
        chart_left, chart_top, chart_right, chart_bottom = 720, 310, 1260, 660
        for row in range(5):
            y = chart_top + row * ((chart_bottom - chart_top) // 4)
            draw.line((chart_left, y, chart_right, y), fill="#1C2A3B", width=1)
        values = [42, 34, 25, 18]
        points = []
        for index, value in enumerate(values):
            x = chart_left + index * ((chart_right - chart_left) // 3)
            y = chart_bottom - int((value / 48) * (chart_bottom - chart_top))
            points.append((x, y))
            draw.ellipse((x - 8, y - 8, x + 8, y + 8), fill=accent)
            draw.text((x - 18, chart_bottom + 24), chr(65 + index), fill="#6F8095", font=_font(17, bold=True))
        draw.line(points, fill=accent, width=5, joint="curve")
        draw.text((710, 700), "Local synthetic data • 4 passes", fill="#6F8095", font=_font(18))

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


def _v4_fixture_scenes(story: dict, format_name: str) -> list[dict]:
    channel_id = story["channel_id"]
    energetic = channel_id == "lobbysignal"
    scenes = [dict(scene) for scene in story[format_name]["scenes"]]
    transition_sequence = (
        ["whip_pan", "match_cut", "glitch_rgb_split", "liquid_displacement", "smash_cut", "cross_dissolve"]
        if energetic
        else ["whoosh_zoom", "match_cut", "cross_dissolve", "match_cut", "whoosh_zoom", "cross_dissolve"]
    )
    for index, scene in enumerate(scenes):
        scene_type = scene["scene_type"]
        if scene_type == "source_browser":
            scene["shot_style"] = "source_full"
            scene["camera"] = {
                "preset": "handheld_micro" if energetic else "dolly_in",
                "intensity": 1.05 if energetic else 0.72,
                "target": {"x": 0.58, "y": 0.36},
            }
            scene["micro_beats"] = [
                {"at": 0.85, "kind": "callout"},
                {"at": 1.65, "kind": "crop_shift"},
                {"at": 2.6, "kind": "tag_pop"},
            ]
            scene["effects"] = [
                {"kind": "rule_of_thirds_reframe", "x": 0.58, "y": 0.36, "strength": 0.5},
                {"kind": "light_leak", "opacity": 0.12 if energetic else 0.08},
            ]
            scene["audio_cues"] = [
                {"at": 0.1, "kind": "whoosh", "volume": 0.15 if energetic else 0.11},
                {"at": 1.55, "kind": "click", "volume": 0.08},
            ]
        elif scene_type == "stat":
            value = scene.get("data", {}).get("value", 0)
            suffix = scene.get("data", {}).get("suffix", "")
            scene["shot_style"] = "kinetic_text"
            scene["camera"] = {"preset": "rack_push", "intensity": 0.86 if energetic else 0.62}
            scene["micro_beats"] = [
                {"at": 0.75, "kind": "focus_punch"},
                {"at": 1.45, "kind": "underline"},
            ]
            scene["effects"] = [
                {
                    "kind": "stat_count_up",
                    "final_value": value,
                    "verified_value": value,
                    "suffix": suffix,
                },
                {"kind": "lens_flare", "strength": 0.18 if energetic else 0.11},
            ]
            scene["audio_cues"] = [
                {"at": 0.62, "kind": "lowpass", "duration": 0.58},
                {"at": 1.0, "kind": "ding", "volume": 0.11},
            ]
        elif scene_type == "chart":
            scene["shot_style"] = "data_full"
            scene["camera"] = {"preset": "crane_down", "intensity": 0.82 if energetic else 0.58}
            scene["micro_beats"] = [
                {"at": 0.8, "kind": "underline"},
                {"at": 1.7, "kind": "focus_punch"},
                {"at": 2.5, "kind": "flash"},
            ]
            scene["effects"] = [
                {"kind": "film_grain"},
                {"kind": "vignette_pulse"},
            ]
            scene["audio_cues"] = [
                {"at": 0.55, "kind": "riser", "volume": 0.09 if energetic else 0.065},
                {"at": 1.65, "kind": "impact", "volume": 0.12 if energetic else 0.085},
            ]
        elif scene_type == "timeline":
            scene["shot_style"] = "graphic_3d"
            scene["camera"] = {
                "preset": "orbit_right" if energetic else "orbit_left",
                "intensity": 1.0 if energetic else 0.7,
            }
            scene["micro_beats"] = [
                {"at": 0.9, "kind": "tag_pop"},
                {"at": 2.0, "kind": "focus_punch"},
            ]
            scene["effects"] = [
                {"kind": "icon_morph", "from": "plus", "to": "diamond", "size": 112},
                {"kind": "chromatic_pulse"} if energetic else {"kind": "light_leak", "opacity": 0.08},
            ]
            scene["audio_cues"] = [
                {"at": 0.5, "kind": "whoosh", "volume": 0.13 if energetic else 0.09},
                {"at": 1.8, "kind": "click", "volume": 0.08},
            ]
        elif scene_type in {"comparison", "before_after"}:
            scene["shot_style"] = "split_screen"
            scene["camera"] = {"preset": "dolly_out", "intensity": 0.82 if energetic else 0.55}
            scene["micro_beats"] = [
                {"at": 0.75, "kind": "crop_shift"},
                {"at": 1.6, "kind": "focus_punch"},
            ]
            scene["effects"] = [
                {"kind": "particle_burst", "at": 0.28, "count": 22 if energetic else 14},
                {"kind": "duotone_flash"} if energetic else {"kind": "underline_sweep"},
            ]
            scene["audio_cues"] = [
                {"at": 0.55, "kind": "riser", "volume": 0.10 if energetic else 0.07},
                {"at": 1.45, "kind": "impact", "volume": 0.14 if energetic else 0.095},
            ]
        else:
            scene["shot_style"] = "kinetic_text"
            scene["camera"] = {
                "preset": "whip_pan" if energetic else "rack_push",
                "intensity": 0.95 if energetic else 0.6,
            }
            scene["micro_beats"] = [
                {"at": 0.75, "kind": "underline"},
                {"at": 1.55, "kind": "tag_pop"},
            ]
            scene["effects"] = [
                {"kind": "scanline_flicker"} if energetic else {"kind": "film_grain"},
            ]
            scene["audio_cues"] = [
                {"at": 0.3, "kind": "braam", "volume": 0.09 if energetic else 0.065},
            ]

        scene["transition_out"] = transition_sequence[min(index, len(transition_sequence) - 1)]
        if index % 3 == 0:
            scene["cut_bias"] = "visual_lead"
            scene["cut_offset_seconds"] = 0.16 if energetic else 0.12
        elif index % 3 == 1:
            scene["cut_bias"] = "audio_lead"
            scene["cut_offset_seconds"] = 0.13 if energetic else 0.10
        else:
            scene["cut_bias"] = "neutral"
            scene["cut_offset_seconds"] = 0.0
    return scenes


def _scene_plan(story: dict, format_name: str):
    return parse_scene_plan(
        {
            "channel_id": story["channel_id"],
            "format": "longform" if format_name == "long" else "short",
            "scenes": _v4_fixture_scenes(story, format_name),
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
