from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import pytest

from app.assets.manifest import sha256_file, write_asset_manifest
from app.assets.models import AssetManifest, AssetRecord


def _record(path: Path, *, asset_id: str = "source-1", scene_id: str | None = None) -> AssetRecord:
    return AssetRecord(
        id=asset_id,
        kind="source_screenshot",
        local_path=str(path),
        source_url="https://example.com/source",
        source_name="Example",
        usage="scene evidence",
        license_note="source-page screenshot",
        sha256=sha256_file(path),
        captured_at=datetime(2026, 9, 17, 10, 0, tzinfo=timezone.utc),
        scene_id=scene_id,
    )


def test_sha256_file_hashes_actual_bytes(tmp_path: Path):
    asset = tmp_path / "asset.png"
    asset.write_bytes(b"autotube-asset")

    assert sha256_file(asset) == hashlib.sha256(b"autotube-asset").hexdigest()


def test_asset_manifest_rejects_duplicate_ids(tmp_path: Path):
    asset = tmp_path / "asset.png"
    asset.write_bytes(b"x")
    record = _record(asset)

    with pytest.raises(ValueError, match="unique"):
        AssetManifest(records=(record, record))


def test_manifest_preserves_source_url_and_round_trips(tmp_path: Path):
    asset = tmp_path / "asset.png"
    asset.write_bytes(b"image-bytes")
    manifest = AssetManifest(records=(_record(asset, scene_id="scene-7"),))

    out = write_asset_manifest(manifest.records, tmp_path / "asset-manifest.json")
    payload = json.loads(out.read_text(encoding="utf-8"))

    assert payload["records"][0]["source_url"] == "https://example.com/source"
    assert payload["records"][0]["scene_id"] == "scene-7"
    assert payload["records"][0]["sha256"] == sha256_file(asset)
    assert AssetManifest.from_dict(payload) == manifest
