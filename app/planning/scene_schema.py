from __future__ import annotations

from dataclasses import dataclass, field


SCENE_TYPES = {
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
    "fallback_editorial",
}

MOTIONS = {"none", "fade", "push_left", "push_up", "slow_zoom", "punch_in", "parallax"}
TRANSITIONS = {"cut", "crossfade", "wipe", "slide", "stinger"}
FORMATS = {"longform", "short"}


@dataclass(frozen=True)
class SceneSpec:
    id: str
    narration: str
    purpose: str
    scene_type: str
    headline: str = ""
    subheadline: str = ""
    source_ids: tuple[str, ...] = ()
    asset_ids: tuple[str, ...] = ()
    motion: str = "none"
    emphasis: tuple[str, ...] = ()
    transition: str = "cut"
    fallback_scene_type: str = "fallback_editorial"
    data: dict = field(default_factory=dict)


@dataclass(frozen=True)
class ScenePlan:
    channel_id: str
    format: str
    scenes: tuple[SceneSpec, ...]
    schema_version: str = "1"


def _parse_scene(row: dict) -> SceneSpec:
    scene_id = str(row.get("id", "")).strip()
    narration = str(row.get("narration", "")).strip()
    scene_type = str(row.get("scene_type", "")).strip()
    motion = str(row.get("motion", "none")).strip()
    transition = str(row.get("transition", "cut")).strip()
    fallback = str(row.get("fallback_scene_type", "fallback_editorial")).strip()

    if not scene_id:
        raise ValueError("scene id is required")
    if not narration:
        raise ValueError(f"scene {scene_id} narration is required")
    if scene_type not in SCENE_TYPES:
        raise ValueError(f"unknown scene type: {scene_type}")
    if motion not in MOTIONS:
        raise ValueError(f"unknown motion preset: {motion}")
    if transition not in TRANSITIONS:
        raise ValueError(f"unknown transition: {transition}")
    if fallback not in SCENE_TYPES:
        raise ValueError(f"unknown fallback scene type: {fallback}")

    return SceneSpec(
        id=scene_id,
        narration=narration,
        purpose=str(row.get("purpose", "")).strip(),
        scene_type=scene_type,
        headline=str(row.get("headline", "")).strip(),
        subheadline=str(row.get("subheadline", "")).strip(),
        source_ids=tuple(str(x) for x in row.get("source_ids", [])),
        asset_ids=tuple(str(x) for x in row.get("asset_ids", [])),
        motion=motion,
        emphasis=tuple(str(x) for x in row.get("emphasis", [])),
        transition=transition,
        fallback_scene_type=fallback,
        data=dict(row.get("data", {})),
    )


def parse_scene_plan(payload: dict) -> ScenePlan:
    channel_id = str(payload.get("channel_id", "")).strip()
    plan_format = str(payload.get("format", "")).strip()
    schema_version = str(payload.get("schema_version", "1")).strip()
    rows = payload.get("scenes", [])

    if not channel_id:
        raise ValueError("channel_id is required")
    if plan_format not in FORMATS:
        raise ValueError(f"unknown scene-plan format: {plan_format}")
    if not isinstance(rows, list) or not rows:
        raise ValueError("scene plan requires at least one scene")

    scenes = tuple(_parse_scene(row) for row in rows)
    ids = [scene.id for scene in scenes]
    if len(set(ids)) != len(ids):
        raise ValueError("scene ids must be unique")

    return ScenePlan(channel_id, plan_format, scenes, schema_version)
