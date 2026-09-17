from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class NarrationSegment:
    text: str
    raw_path: Path
    normalized_path: Path
    duration: float
    backend: str
    voice_profile: str

    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "raw_path": str(self.raw_path),
            "normalized_path": str(self.normalized_path),
            "duration": self.duration,
            "backend": self.backend,
            "voice_profile": self.voice_profile,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "NarrationSegment":
        return cls(
            text=data["text"],
            raw_path=Path(data["raw_path"]),
            normalized_path=Path(data["normalized_path"]),
            duration=float(data["duration"]),
            backend=data["backend"],
            voice_profile=data["voice_profile"],
        )


@dataclass(frozen=True)
class NarrationTrack:
    path: Path
    segments: tuple[NarrationSegment, ...]
    duration: float

    def to_dict(self) -> dict:
        return {
            "path": str(self.path),
            "segments": [segment.to_dict() for segment in self.segments],
            "duration": self.duration,
        }
