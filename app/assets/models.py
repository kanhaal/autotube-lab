from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class AssetRecord:
    id: str
    kind: str
    local_path: str
    source_url: str | None
    source_name: str | None
    usage: str
    license_note: str | None
    sha256: str
    captured_at: datetime
    scene_id: str | None = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "kind": self.kind,
            "local_path": self.local_path,
            "source_url": self.source_url,
            "source_name": self.source_name,
            "usage": self.usage,
            "license_note": self.license_note,
            "sha256": self.sha256,
            "captured_at": self.captured_at.isoformat(),
            "scene_id": self.scene_id,
        }

    @classmethod
    def from_dict(cls, payload: dict) -> "AssetRecord":
        return cls(
            id=payload["id"],
            kind=payload["kind"],
            local_path=payload["local_path"],
            source_url=payload.get("source_url"),
            source_name=payload.get("source_name"),
            usage=payload["usage"],
            license_note=payload.get("license_note"),
            sha256=payload["sha256"],
            captured_at=datetime.fromisoformat(payload["captured_at"]),
            scene_id=payload.get("scene_id"),
        )


@dataclass(frozen=True)
class AssetManifest:
    records: tuple[AssetRecord, ...]
    schema_version: str = "1"

    def __post_init__(self) -> None:
        ids = [record.id for record in self.records]
        if len(ids) != len(set(ids)):
            raise ValueError("asset ids must be unique")

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "records": [record.to_dict() for record in self.records],
        }

    @classmethod
    def from_dict(cls, payload: dict) -> "AssetManifest":
        return cls(
            records=tuple(AssetRecord.from_dict(item) for item in payload.get("records", [])),
            schema_version=str(payload.get("schema_version", "1")),
        )
