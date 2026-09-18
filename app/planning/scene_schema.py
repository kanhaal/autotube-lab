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
TRANSITION_OUTS = {"glitch_rgb_split", "whoosh_zoom"}
FORMATS = {"longform", "short"}

EFFECT_KINDS = {
    "auto_zoom",
    "spotlight_dim",
    "cursor_smooth",
    "code_typewriter",
    "stat_count_up",
    "split_compare",
    "speed_ramp",
    "scroll_reveal",
    "tier_list",
    "vs_screen",
    "ticker_overlay",
    "meme_flash",
    "freeze_frame",
    "kinetic_word_reveal",
    # Optional V3.5 motion/VFX vocabulary. These remain render-layer requests only.
    "kinetic_infographic",
    "progress_reveal",
    "icon_morph",
    "tag_pop",
    "parallax_layers",
    "grid_reveal",
    "card_flip",
    "underline_sweep",
    "leader_line",
    "waveform_overlay",
    "chromatic_pulse",
    "light_leak",
    "film_grain",
    "vignette_pulse",
    "rack_focus",
    "particle_burst",
    "screen_shake",
    "scanline_flicker",
    "duotone_flash",
    "lower_third",
    "intro_sting",
    "chapter_card",
}


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
    effects: tuple[dict[str, Any], ...] = ()
    transition_out: str | None = None


@dataclass(frozen=True)
class ScenePlan:
    channel_id: str
    format: str
    scenes: tuple[SceneSpec, ...]
    schema_version: str = "1"


def _effects(scene_id: str, payload: object) -> tuple[dict[str, Any], ...]:
    if payload is None:
        return ()
    if not isinstance(payload, list):
        raise ValueError(f"scene {scene_id} effects must be an array")

    normalized: list[dict[str, Any]] = []
    for index, item in enumerate(payload):
        if not isinstance(item, dict):
            raise ValueError(f"scene {scene_id} effect {index} must be an object")
        kind = str(item.get("kind", "")).strip()
        if kind not in EFFECT_KINDS:
            raise ValueError(f"unsupported effect kind: {kind}")
        normalized.append(dict(item))
    return tuple(normalized)


def _scene(payload: dict) -> SceneSpec:
    scene_id = str(payload.get("id", "")).strip()
    narration = str(payload.get("narration", "")).strip()
    scene_type = str(payload.get("scene_type", "")).strip()
    motion = str(payload.get("motion", "none")).strip()
    transition = str(payload.get("transition", "cut")).strip()
    fallback = str(payload.get("fallback_scene_type", "fallback_editorial")).strip()
    raw_transition_out = payload.get("transition_out")
    transition_out = None if raw_transition_out in {None, ""} else str(raw_transition_out).strip()

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
    if transition_out is not None and transition_out not in TRANSITION_OUTS:
        raise ValueError(f"unsupported transition_out: {transition_out}")
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
        effects=_effects(scene_id, payload.get("effects", [])),
        transition_out=transition_out,
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
