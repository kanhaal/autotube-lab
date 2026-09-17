from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CaptionCue:
    start: float
    end: float
    text: str
    words: tuple[str, ...]
