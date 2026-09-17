from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping

from app.quality.models import QualityReport

ProductionState = dict[str, Any]
StageResult = Mapping[str, Any] | None
Stage = Callable[[ProductionState], StageResult]


@dataclass(frozen=True)
class ProductionStages:
    editorial: Stage
    assets: Stage
    narration: Stage
    captions: Stage
    audio: Stage
    render: Stage
    thumbnails: Stage
    qa: Stage


@dataclass(frozen=True)
class ProductionResult:
    state: ProductionState
    quality_report: QualityReport

    @property
    def publishable(self) -> bool:
        return self.quality_report.ok


_STAGE_NAMES = (
    "editorial",
    "assets",
    "narration",
    "captions",
    "audio",
    "render",
    "thumbnails",
    "qa",
)


def produce_episode(seed: Mapping[str, Any], stages: ProductionStages) -> ProductionResult:
    """Run the professional production stages in their fixed production order."""

    state: ProductionState = dict(seed)
    for name in _STAGE_NAMES:
        update = getattr(stages, name)(state)
        if update is not None:
            state.update(dict(update))

    report = state.get("quality_report")
    if not isinstance(report, QualityReport):
        raise TypeError("qa stage must provide a QualityReport as quality_report")
    return ProductionResult(state=state, quality_report=report)
