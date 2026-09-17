from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

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
    data: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ScenePlan:
    channel_id: str
    format: str
    scenes: tuple[SceneSpec, ...]
    schema_version: str = "1"


def _scene(payload: dict) -> SceneSpec:
    scene_id = str(payload.get("id", "")).strip()
    narration = str(payload.get("narration", "")).strip()
    scene_type = str(payload.get("scene_type", "")).strip()
    motion = str(payload.get("motion", "none")).strip()
    transition = str(payload.get("transition", "cut")).strip()
    fallback = str(payload.get("fallback_scene_type", "fallback_editorial")).strip()

    if not scene_id:
        raise ValueError("scene id is required")
    if not narration:
        raise ValueError(f"scene {scene_id} narration is required")
    if scene_type not in SCENE_TYPES:
        raise ValueError(f"unsupported scene_type: {scene_type}")
    if motion not in MOTIONS:
        raise ValueError(f"unsupported motion: {motion}")
    if transition not in TRANSITIONS:
        raise ValueError(f"unsupported transition: {transition}")
    if fallback not in SCENE_TYPES:
        raise ValueError(f"unsupported fallback_scene_type: {fallback}")

    data = payload.get("data", {})
    if not isinstance(data, dict):
        raise ValueError(f"scene {scene_id} data must be an object")

    return SceneSpec(
        id=scene_id,
        narration=narration,
        purpose=str(payload.get("purpose", "")).strip(),
        scene_type=scene_type,
        headline=str(payload.get("headline", "")).strip(),
        subheadline=str(payload.get("subheadline", "")).strip(),
        source_ids=tuple(str(x) for x in payload.get("source_ids", [])),
        asset_ids=tuple(str(x) for x in payload.get("asset_ids", [])),
        motion=motion,
        emphasis=tuple(str(x) for x in payload.get("emphasis", [])),
        transition=transition,
        fallback_scene_type=fallback,
        data=data,
    )


def parse_scene_plan(payload: dict) -> ScenePlan:
    channel_id = str(payload.get("channel_id", "")).strip()
    format_name = str(payload.get("format", "")).strip()
    raw_scenes = payload.get("scenes")

    if not channel_id:
        raise ValueError("channel_id is required")
    if format_name not in FORMATS:
        raise ValueError(f"unsupported format: {format_name}")
    if not isinstance(raw_scenes, list) or not raw_scenes:
        raise ValueError("scene plan requires at least one scene")

    scenes = tuple(_scene(item) for item in raw_scenes)
    ids = [scene.id for scene in scenes]
    if len(ids) != len(set(ids)):
        raise ValueError("scene ids must be unique")

    return ScenePlan(channel_id=channel_id, format=format_name, scenes=scenes)
