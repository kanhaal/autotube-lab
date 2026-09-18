from __future__ import annotations

import hashlib
import json
import tempfile
import wave
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

from app.assets.models import AssetManifest, AssetRecord
from app.captions.models import CaptionCue
from app.config import channel_config
from app.planning.scene_schema import parse_scene_plan
from app.rendering.package import build_render_package
from app.rendering.pipeline import composition_id
from app.rendering.runner import RemotionRunner


def _wav(path: Path, seconds: int) -> Path:
    sample_rate = 48000
    silence = b"\x00\x00" * sample_rate
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        for _ in range(seconds):
            wav.writeframesraw(silence)
        wav.writeframes(b"")
    return path


def _png(path: Path, color: str) -> Path:
    Image.new("RGB", (1440, 900), color).save(path)
    return path


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    fixture = json.loads(
        Path("tests/fixtures/media/kernelrush_story.json").read_text(encoding="utf-8")
    )
    cfg = channel_config("kernelrush")

    with tempfile.TemporaryDirectory(prefix="autotube-windows-render-") as tmp:
        root = Path(tmp)
        source = _png(root / "source-card.png", "#123456")
        fallback = _png(root / "fallback-card.png", "#223344")
        audio = _wav(root / "master.wav", 42)

        plan = parse_scene_plan(
            {
                "channel_id": fixture["channel_id"],
                "format": "longform",
                "scenes": fixture["long"]["scenes"],
            }
        )
        captions = tuple(
            CaptionCue(
                float(cue["start"]),
                float(cue["end"]),
                cue["text"],
                tuple(cue["text"].split()),
            )
            for cue in fixture["long"]["captions"]
        )
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
                print(log.read_text(encoding="utf-8", errors="replace"))
            raise

        if not out.is_file() or out.stat().st_size <= 0:
            raise RuntimeError("Windows real-package smoke did not produce a non-empty video")
        print(f"Rendered {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
