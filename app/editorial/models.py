from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HookCandidate:
    text: str
    specificity: float
    curiosity: float
    clarity: float
    brevity: float
    fact_supported: bool

    @property
    def score(self) -> float:
        return (self.specificity + self.curiosity + self.clarity + self.brevity) / 4


@dataclass(frozen=True)
class EditorialOutline:
    strongest_signal: str
    what_changed: str
    why_now: str
    context: tuple[str, ...]
    evidence_order: tuple[str, ...]
    tension: str
    implication: str
    uncertainty: str
    closing_takeaway: str


@dataclass(frozen=True)
class Critique:
    needs_rewrite: bool
    opening_strength: float
    information_density: float
    logical_flow: float
    redundancy: float
    factual_discipline: float
    pacing: float
    clarity: float
    emotional_rhythm: float
    payoff: float
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class EditorialBundle:
    outline: EditorialOutline
    hooks: tuple[HookCandidate, HookCandidate, HookCandidate]
    selected_hook: HookCandidate
    draft_script: str
    critique: Critique
    script: str
