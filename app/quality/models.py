from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class QualityIssue:
    code: str
    message: str
    fatal: bool = True


@dataclass(frozen=True)
class QualityReport:
    ok: bool
    issues: tuple[QualityIssue, ...]
