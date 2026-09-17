from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class AudioAsset:
    id: str
    path: Path
    kind: str
    channels: tuple[str, ...]
    moods: tuple[str, ...]
    license_note: str
    source_url: str | None


class AudioLibrary:
    def __init__(self, assets: tuple[AudioAsset, ...]):
        self.assets = assets

    @classmethod
    def from_yaml(cls, path: Path) -> "AudioLibrary":
        path = Path(path)
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        assets = []
        for raw in data.get("assets", []):
            asset_path = Path(raw["path"])
            if not asset_path.is_absolute():
                asset_path = path.parent / asset_path
            assets.append(
                AudioAsset(
                    id=str(raw["id"]),
                    path=asset_path,
                    kind=str(raw["kind"]),
                    channels=tuple(raw.get("channels", ())),
                    moods=tuple(raw.get("moods", ())),
                    license_note=str(raw.get("license_note", "")),
                    source_url=raw.get("source_url"),
                )
            )
        return cls(tuple(assets))

    def select(self, kind: str, channel_id: str, mood: str) -> AudioAsset | None:
        candidates = [
            asset
            for asset in self.assets
            if asset.kind == kind
            and asset.path.exists()
            and (not asset.channels or channel_id in asset.channels)
            and (not asset.moods or mood in asset.moods)
        ]
        return sorted(candidates, key=lambda item: item.id)[0] if candidates else None
