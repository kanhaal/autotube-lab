from __future__ import annotations

import os
import re

from app.quality.models import QualityIssue

_HEADLINE_REQUIRED = {
    "hook",
    "headline",
    "source_browser",
    "device",
    "github",
    "game_store",
    "stat",
    "chart",
    "timeline",
    "before_after",
    "comparison",
    "quote",
    "list",
    "process",
    "code",
    "map",
    "social_context",
    "chapter",
    "conclusion",
}
_ASSET_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
_SAFE_X = (0.05, 0.95)
_SAFE_Y = (0.08, 0.92)
_DEFAULT_MAX_REPEAT = 3


def _max_repeat() -> int:
    try:
        return max(1, int(os.getenv("AUTOTUBE_MAX_REPEAT_SCENE_TYPE", str(_DEFAULT_MAX_REPEAT))))
    except ValueError:
        return _DEFAULT_MAX_REPEAT


def _number(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def validate_scene_layout_metadata(scene_plan, channel_id: str) -> tuple[QualityIssue, ...]:
    issues: list[QualityIssue] = []
    if str(scene_plan.channel_id).strip().lower() != str(channel_id).strip().lower():
        issues.append(
            QualityIssue(
                "channel_mismatch",
                f"scene plan channel {scene_plan.channel_id!r} does not match {channel_id!r}",
            )
        )

    previous_type: str | None = None
    repeated = 0
    max_repeat = _max_repeat()

    for scene in scene_plan.scenes:
        if scene.scene_type in _HEADLINE_REQUIRED and not scene.headline.strip():
            issues.append(
                QualityIssue("empty_headline", f"scene {scene.id} requires a non-empty headline")
            )

        if scene.scene_type == previous_type:
            repeated += 1
        else:
            previous_type = scene.scene_type
            repeated = 1
        if repeated == max_repeat + 1:
            issues.append(
                QualityIssue(
                    "repeated_layout",
                    f"scene type {scene.scene_type!r} repeats more than {max_repeat} times consecutively",
                )
            )

        for asset_id in scene.asset_ids:
            if not _ASSET_ID.fullmatch(asset_id.strip()):
                issues.append(
                    QualityIssue(
                        "invalid_asset_id",
                        f"scene {scene.id} has invalid asset id {asset_id!r}",
                    )
                )

        position = scene.data.get("caption_position")
        if position is not None:
            if not isinstance(position, dict):
                issues.append(
                    QualityIssue(
                        "caption_outside_safe_area",
                        f"scene {scene.id} caption_position must contain normalized x/y coordinates",
                    )
                )
                continue
            x = _number(position.get("x"))
            y = _number(position.get("y"))
            if (
                x is None
                or y is None
                or not (_SAFE_X[0] <= x <= _SAFE_X[1])
                or not (_SAFE_Y[0] <= y <= _SAFE_Y[1])
            ):
                issues.append(
                    QualityIssue(
                        "caption_outside_safe_area",
                        f"scene {scene.id} caption_position is outside normalized safe coordinates",
                    )
                )

    return tuple(issues)
