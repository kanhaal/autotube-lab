from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.assets.manifest import sha256_file
from app.assets.models import AssetRecord
from app.assets.service import AssetPreparationError, prepare_assets
from app.planning.scene_schema import ScenePlan, SceneSpec


CHANNEL = {
    "name": "KernelRush",
    "brand": {
        "background": "#0A0D12",
        "foreground": "#F5F7FA",
        "accent": "#5EF2C2",
        "secondary": "#7AA2FF",
    },
}

PACKET = {
    "sources": [
        {"source_name": "Alpha", "url": "https://example.com/alpha", "text": "Alpha launched."},
        {"source_name": "Beta", "url": "https://example.com/beta", "text": "Beta confirmed it."},
    ]
}


class FakeCapturer:
    def __init__(self, fail_urls=()):
        self.fail_urls = set(fail_urls)
        self.calls = []

    def capture(self, request, out_dir: Path):
        self.calls.append(request.source_url)
        if request.source_url in self.fail_urls:
            raise RuntimeError("capture failed")
        out = Path(out_dir) / f"{request.id}.png"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(b"captured")
        return AssetRecord(
            id=request.id,
            kind=request.kind,
            local_path=str(out),
            source_url=request.source_url,
            source_name=request.source_name,
            usage=request.purpose,
            license_note="source-page screenshot",
            sha256=sha256_file(out),
            captured_at=datetime.now(timezone.utc),
        )


def _source(scene_id, url, purpose, *, required=False):
    return SceneSpec(
        id=scene_id,
        narration="Source narration.",
        purpose=purpose,
        scene_type="source_browser",
        headline="SOURCE",
        data={"source_url": url, "asset_required": required},
    )


def test_prepare_assets_captures_sources_falls_back_and_writes_manifest(tmp_path: Path):
    scenes = (
        _source("s1", "https://example.com/alpha", "primary evidence"),
        _source("s2", "https://example.com/beta", "secondary evidence"),
        SceneSpec(
            id="s3",
            narration="Why it matters.",
            purpose="editorial explanation",
            scene_type="fallback_editorial",
            headline="WHY IT MATTERS",
        ),
    )
    plan = ScenePlan(channel_id="kernelrush", format="longform", scenes=scenes)
    capturer = FakeCapturer(fail_urls={"https://example.com/beta"})

    manifest = prepare_assets(plan, PACKET, CHANNEL, tmp_path, capturer)

    assert len(manifest.records) == 3
    assert manifest.records[0].source_url == "https://example.com/alpha"
    assert manifest.records[1].source_url is None
    assert manifest.records[1].id == "fallback-s2"
    assert manifest.records[2].id == "fallback-s3"
    assert all(Path(record.local_path).exists() for record in manifest.records)
    assert (tmp_path / "asset-manifest.json").exists()


def test_prepare_assets_blocks_failed_required_capture(tmp_path: Path):
    plan = ScenePlan(
        channel_id="kernelrush",
        format="longform",
        scenes=(
            _source(
                "s1",
                "https://example.com/alpha",
                "required evidence",
                required=True,
            ),
        ),
    )

    with pytest.raises(AssetPreparationError, match="required asset"):
        prepare_assets(
            plan,
            PACKET,
            CHANNEL,
            tmp_path,
            FakeCapturer(fail_urls={"https://example.com/alpha"}),
        )


def test_prepare_assets_deduplicates_same_url_and_purpose(tmp_path: Path):
    plan = ScenePlan(
        channel_id="kernelrush",
        format="longform",
        scenes=(
            _source("s1", "https://example.com/alpha", "same evidence"),
            _source("s2", "https://example.com/alpha", "same evidence"),
        ),
    )
    capturer = FakeCapturer()

    manifest = prepare_assets(plan, PACKET, CHANNEL, tmp_path, capturer)

    assert capturer.calls == ["https://example.com/alpha"]
    assert len(manifest.records) == 1
