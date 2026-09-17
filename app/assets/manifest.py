from __future__ import annotations

import hashlib
import json
from pathlib import Path

from app.assets.models import AssetManifest, AssetRecord


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_asset_manifest(records, out: Path) -> Path:
    manifest = AssetManifest(records=tuple(records))
    target = Path(out)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return target
