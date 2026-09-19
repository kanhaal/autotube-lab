from __future__ import annotations

import hashlib
import json
import math
import struct
import tempfile
import wave
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

from app.assets.models import AssetManifest, AssetRecord
from app.audio.mix import SfxEvent, mix_episode_audio
from app.captions.models import CaptionCue, CaptionWord
from app.config import channel_config
from app.planning.scene_schema import parse_scene_plan
from app.rendering.package import build_render_package
from app.rendering.pipeline import composition_id
from app.rendering.runner import RemotionRunner


def _wav(path: Path, seconds: float, frequency: float = 220.0) -> Path:
    sample_rate = 48000
    frame_count = int(sample_rate * seconds)
    amplitude = 1200
    frames = bytearray()
    for index in range(frame_count):
        sample = int(amplitude * math.sin(2 * math.pi * frequency * index / sample_rate))
        frames.extend(struct.pack("<h", sample))
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(bytes(frames))
    return path


def _png(path: Path, color: str) -> Path:
    Image.new("RGB", (1440, 900), color).save(path)
    return path


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _caption(cue: dict) -> CaptionCue:
    start = float(cue["start"])
    end = float(cue["end"])
    words = tuple(cue["text"].split())
    duration = max(0.001, end - start)
    timings = tuple(
        CaptionWord(
            word,
            start + duration * (index / len(words)),
            start + duration * ((index + 1) / len(words)),
        )
        for index, word in enumerate(words)
    )
    return CaptionCue(start, end, cue["text"], words, timings)


def main() -> None:
    fixture = json.loads(
        Path("tests/fixtures/media/kernelrush_story.json").read_text(encoding="utf-8")
    )
    cfg = channel_config("kernelrush")

    with tempfile.TemporaryDirectory(prefix="autotube-windows-render-") as tmp:
        root = Path(tmp)
        source = _png(root / "source-card.png", "#123456")
        fallback = _png(root / "fallback-card.png", "#223344")

        narration = _wav(root / "narration.wav", 42, 220)
        music = _wav(root / "music.wav", 45, 92)
        sfx = _wav(root / "sfx.wav", 0.2, 880)
        audio = mix_episode_audio(
            narration,
            music,
            (SfxEvent(sfx, start_ms=6000, volume=0.25),),
            root / "master.wav",
        )

        plan = parse_scene_plan(
            {
                "channel_id": fixture["channel_id"],
                "format": "longform",
                "scenes": fixture["long"]["scenes"],
            }
        )
        captions = tuple(_caption(cue) for cue in fixture["long"]["captions"])
        now = datetime.now(timezone.utc)
        assets = AssetManifest(
            records=(
                AssetRecord(
                    "source-card",
                    "source_screenshot",
                    str(source),
                    None,
                    "Synthetic local source",
                    "evidence",
                    "generated CI fixture",
                    _sha(source),
                    now,
                    "kr-long-source",
                ),
                AssetRecord(
                    "fallback-card",
                    "fallback_editorial",
                    str(fallback),
                    None,
                    None,
                    "fallback",
                    "generated CI fixture",
                    _sha(fallback),
                    now,
                    "kr-long-fallback",
                ),
            )
        )
        script = " ".join(scene.narration for scene in plan.scenes)
        package = build_render_package(
            cfg,
            fixture["title"],
            script,
            plan,
            captions,
            assets,
            audio,
            root / "render-package-long",
            format="long",
        )

        runner = RemotionRunner()
        out = root / "long.mp4"
        try:
            runner.render(package, composition_id("kernelrush", "long"), out)
        except Exception:
            log = root / "remotion-render.log"
            if log.is_file():
                print("\n===== REMOTION LOG =====\n")
                rendered_log = log.read_text(encoding="utf-8", errors="replace")
                print(rendered_log.encode("ascii", "backslashreplace").decode("ascii"))
            raise

        if not out.is_file() or out.stat().st_size <= 0:
            raise RuntimeError("Windows real-package smoke did not produce a non-empty video")
        print(f"Rendered {out} ({out.stat().st_size} bytes)")

        short_narration = _wav(root / "short-narration.wav", 36, 260)
        short_audio = mix_episode_audio(
            short_narration,
            music,
            (SfxEvent(sfx, start_ms=5000, volume=0.22),),
            root / "short-master.wav",
        )
        short_plan = parse_scene_plan(
            {
                "channel_id": fixture["channel_id"],
                "format": "short",
                "scenes": fixture["short"]["scenes"],
            }
        )
        short_captions = tuple(_caption(cue) for cue in fixture["short"]["captions"])
        short_script = " ".join(scene.narration for scene in short_plan.scenes)
        short_package = build_render_package(
            cfg,
            fixture["title"],
            short_script,
            short_plan,
            short_captions,
            assets,
            short_audio,
            root / "render-package-short",
            format="short",
        )
        short_out = root / "short.mp4"
        try:
            runner.render(short_package, composition_id("kernelrush", "short"), short_out)
        except Exception:
            log = root / "remotion-render.log"
            if log.is_file():
                print("\n===== SHORT REMOTION LOG =====\n")
                print(log.read_text(encoding="utf-8", errors="replace"))
            raise

        if not short_out.is_file() or short_out.stat().st_size <= 0:
            raise RuntimeError("Windows real-package Short smoke did not produce a non-empty video")
        print(f"Rendered {short_out} ({short_out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
