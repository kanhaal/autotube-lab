from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.assets.models import AssetManifest, AssetRecord
from app.captions.models import CaptionCue
from app.planning.scene_schema import ScenePlan, SceneSpec
from app.rendering.package import build_render_package


def test_build_render_package_is_self_contained_and_uses_relative_paths(tmp_path: Path):
    source_image = tmp_path / "source.png"
    source_image.write_bytes(b"png-data")
    narration = tmp_path / "narration.wav"
    narration.write_bytes(b"wav-data")

    scene_plan = ScenePlan(
        channel_id="kernelrush",
        format="longform",
        scenes=(
            SceneSpec(
                id="scene-1",
                narration="A verified launch happened.",
                purpose="hook",
                scene_type="source_browser",
                asset_ids=("asset-1",),
            ),
        ),
    )
    captions = (CaptionCue(0.0, 1.2, "A verified launch happened.", ("A", "verified")),)
    assets = AssetManifest(
        records=(
            AssetRecord(
                id="asset-1",
                kind="screenshot",
                local_path=str(source_image),
                source_url="https://example.com/launch",
                source_name="Example",
                usage="scene source",
                license_note="source screenshot",
                sha256="abc123",
                captured_at=datetime.now(timezone.utc),
            ),
        )
    )
    channel_cfg = {
        "id": "kernelrush",
        "name": "KernelRush",
        "brand": {"background": "#050A14", "accent": "#67F5C5"},
    }

    package_dir = build_render_package(
        channel_cfg,
        "Launch story",
        "A verified launch happened.",
        scene_plan,
        captions,
        assets,
        narration,
        tmp_path / "package",
        format="long",
    )

    for name in (
        "manifest.json",
        "script.json",
        "scenes.json",
        "captions.json",
        "asset-manifest.json",
    ):
        assert (package_dir / name).is_file()

    manifest = json.loads((package_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["schema_version"] == "1"
    assert manifest["format"] == "long"
    assert manifest["width"] == 1920
    assert manifest["height"] == 1080
    assert manifest["fps"] == 30
    assert manifest["audio_path"] == "audio/narration.wav"
    assert not Path(manifest["audio_path"]).is_absolute()

    asset_payload = json.loads((package_dir / "asset-manifest.json").read_text(encoding="utf-8"))
    local_path = asset_payload["records"][0]["local_path"]
    assert local_path.startswith("images/")
    assert not Path(local_path).is_absolute()
    assert (package_dir / local_path).read_bytes() == b"png-data"
    assert (package_dir / manifest["audio_path"]).read_bytes() == narration.read_bytes()


def test_build_render_package_rejects_source_paths_that_escape_declared_root(tmp_path: Path):
    outside = tmp_path / "outside.png"
    outside.write_bytes(b"x")
    audio = tmp_path / "audio.wav"
    audio.write_bytes(b"x")
    plan = ScenePlan(
        channel_id="kernelrush",
        format="longform",
        scenes=(SceneSpec("scene-1", "text", "hook", "headline"),),
    )
    assets = AssetManifest(
        records=(
            AssetRecord(
                "asset-1",
                "screenshot",
                str(outside),
                None,
                None,
                "test",
                None,
                "hash",
                datetime.now(timezone.utc),
            ),
        )
    )

    with pytest.raises(ValueError, match="asset_root"):
        build_render_package(
            {"id": "kernelrush", "name": "KernelRush", "brand": {}},
            "Title",
            "text",
            plan,
            (),
            assets,
            audio,
            tmp_path / "package",
            format="long",
            asset_root=tmp_path / "allowed-assets",
        )


def _write_test_wav(path: Path, seconds: float = 1.25) -> Path:
    import wave

    sample_rate = 16000
    frames = int(sample_rate * seconds)
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(b"\x00\x00" * frames)
    return path


def test_build_render_package_rejects_unreadable_audio_before_remotion(tmp_path: Path):
    audio = tmp_path / "broken.wav"
    audio.write_bytes(b"not a wav file")
    plan = ScenePlan(
        channel_id="kernelrush",
        format="longform",
        scenes=(SceneSpec("scene-1", "text", "hook", "headline"),),
    )

    with pytest.raises(ValueError, match="audio"):
        build_render_package(
            {"id": "kernelrush", "name": "KernelRush", "brand": {}},
            "Title",
            "text",
            plan,
            (),
            AssetManifest(records=()),
            audio,
            tmp_path / "package",
            format="long",
        )


def test_build_render_package_records_real_audio_duration(tmp_path: Path):
    audio = _write_test_wav(tmp_path / "audio.wav", 1.25)
    plan = ScenePlan(
        channel_id="kernelrush",
        format="longform",
        scenes=(SceneSpec("scene-1", "text", "hook", "headline"),),
    )

    package = build_render_package(
        {"id": "kernelrush", "name": "KernelRush", "brand": {}},
        "Title",
        "text",
        plan,
        (),
        AssetManifest(records=()),
        audio,
        tmp_path / "package",
        format="long",
    )
    manifest = json.loads((package / "manifest.json").read_text(encoding="utf-8"))

    assert manifest["duration_source"] == "audio"
    assert manifest["duration_seconds"] == pytest.approx(1.25, abs=0.02)
