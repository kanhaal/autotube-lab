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
TRANSITION_OUTS = {"glitch_rgb_split", "whoosh_zoom", "whip_pan", "match_cut", "smash_cut", "cross_dissolve", "liquid_displacement"}
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
    "kinetic_infographic",
    "progress_reveal",
    "tag_pop",
    "parallax_layers",
    "grid_reveal",
    "card_flip",
    "underline_sweep",
    "callout_leader_line",
    "waveform_overlay",
    "chromatic_pulse",
    "film_grain",
    "vignette_pulse",
    "rack_focus",
    "screen_shake",
    "scanline_flicker",
    "duotone_flash",
    "light_leak",
    "lens_flare",
    "particle_burst",
    "icon_morph",
    "split_screen_multi_angle",
    "rule_of_thirds_reframe",
    "ken_burns",
}
SHOT_STYLES = {
    "source_full",
    "source_detail",
    "kinetic_text",
    "data_full",
    "graphic_3d",
    "split_screen",
    "chapter",
    "editorial",
}
CAMERA_PRESETS = {
    "locked",
    "dolly_in",
    "dolly_out",
    "orbit_left",
    "orbit_right",
    "whip_pan",
    "handheld_micro",
    "rack_push",
    "crane_down",
}
AUDIO_CUE_KINDS = {"whoosh", "impact", "click", "riser", "braam", "ding", "glitch", "static"}
MICRO_BEAT_KINDS = {"focus_punch", "callout", "tag_pop", "underline", "flash", "shake", "crop_shift"}
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
    effects: tuple[dict[str, Any], ...] = ()
    transition_out: str | None = None
    shot_style: str | None = None
    camera: dict[str, Any] = field(default_factory=dict)
    micro_beats: tuple[dict[str, Any], ...] = ()
    audio_cues: tuple[dict[str, Any], ...] = ()


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
    for item in payload:
        if not isinstance(item, dict):
            raise ValueError(f"scene {scene_id} effect must be an object")
        kind = str(item.get("kind", "")).strip()
        if kind not in EFFECT_KINDS:
            raise ValueError(f"unsupported effect kind: {kind}")
        normalized.append(dict(item))
    return tuple(normalized)


def _object_list(
    scene_id: str,
    name: str,
    payload: object,
    *,
    allowed_kinds: set[str] | None = None,
) -> tuple[dict[str, Any], ...]:
    if payload is None:
        return ()
    if not isinstance(payload, list):
        raise ValueError(f"scene {scene_id} {name} must be an array")
    normalized: list[dict[str, Any]] = []
    for item in payload:
        if not isinstance(item, dict):
            raise ValueError(f"scene {scene_id} {name} item must be an object")
        copied = dict(item)
        if allowed_kinds is not None:
            kind = str(copied.get("kind", "")).strip()
            if kind not in allowed_kinds:
                raise ValueError(f"unsupported {name} kind: {kind}")
        normalized.append(copied)
    return tuple(normalized)


def _camera(scene_id: str, payload: object) -> dict[str, Any]:
    if payload is None:
        return {}
    if not isinstance(payload, dict):
        raise ValueError(f"scene {scene_id} camera must be an object")
    copied = dict(payload)
    preset = str(copied.get("preset", "locked")).strip()
    if preset not in CAMERA_PRESETS:
        raise ValueError(f"unsupported camera preset: {preset}")
    copied["preset"] = preset
    return copied


def _scene(payload: dict) -> SceneSpec:
    scene_id = str(payload.get("id", "")).strip()
    narration = str(payload.get("narration", "")).strip()
    scene_type = str(payload.get("scene_type", "")).strip()
    motion = str(payload.get("motion", "none")).strip()
    transition = str(payload.get("transition", "cut")).strip()
    fallback = str(payload.get("fallback_scene_type", "fallback_editorial")).strip()
    transition_out_raw = payload.get("transition_out")
    transition_out = str(transition_out_raw).strip() if transition_out_raw is not None else None
    shot_style_raw = payload.get("shot_style")
    shot_style = str(shot_style_raw).strip() if shot_style_raw is not None else None

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
    if shot_style is not None and shot_style not in SHOT_STYLES:
        raise ValueError(f"unsupported shot_style: {shot_style}")
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
        effects=_effects(scene_id, payload.get("effects")),
        transition_out=transition_out,
        shot_style=shot_style,
        camera=_camera(scene_id, payload.get("camera")),
        micro_beats=_object_list(
            scene_id,
            "micro_beats",
            payload.get("micro_beats"),
            allowed_kinds=MICRO_BEAT_KINDS,
        ),
        audio_cues=_object_list(
            scene_id,
            "audio_cues",
            payload.get("audio_cues"),
            allowed_kinds=AUDIO_CUE_KINDS,
        ),
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
