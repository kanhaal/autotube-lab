from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CaptionWord:
    text: str
    start: float
    end: float


@dataclass(frozen=True)
class CaptionCue:
    start: float
    end: float
    text: str
    words: tuple[str, ...]
    word_timings: tuple[CaptionWord, ...] = ()
