from __future__ import annotations

from app.planning.scene_schema import (
    AUDIO_CUE_KINDS,
    CAMERA_PRESETS,
    CUT_BIASES,
    EFFECT_KINDS,
    MICRO_BEAT_KINDS,
    MOTIONS,
    SCENE_TYPES,
    SHOT_STYLES,
    TRANSITIONS,
    TRANSITION_OUTS,
    ScenePlan,
    parse_scene_plan,
)

REPAIR_PROMPT = (
    "Return one valid JSON object matching the requested scene-plan schema. "
    "Use only registered scene, shot, camera, motion, transition, effect, micro-beat, and audio values."
)

COMMON = """You are the visual director for a factual faceless YouTube explainer.
Use ONLY the supplied approved script and research packet. Do not invent visual facts, statistics,
quotes, products, interfaces, or source claims. Prefer verified source media, full-screen browser/UI
captures, gameplay/B-roll, meaningful detail crops, and original motion graphics over generic imagery.
Use cards only when a contained UI object is editorially clearer than a full-frame shot.
Return JSON with channel_id, format='longform', and scenes. Each scene must contain id, narration,
purpose, scene_type, headline, subheadline, source_ids, asset_ids, motion, emphasis, transition,
fallback_scene_type, and data. V4 scenes MAY also include shot_style, camera, micro_beats,
audio_cues, effects, transition_out, cut_bias, and cut_offset_seconds.

Edit like a professional YouTube editor, not a presentation designer:
- Alternate visual grammar. Do not repeat the same headline-plus-card layout in consecutive scenes.
- Prefer full-bleed verified source media, detail crops, kinetic text beats, split screens, data-full
  shots, and 3D graphic stages. Use editorial card layouts only when they are the clearest choice.
- Keep a meaningful visual event roughly every 0.8-1.8 seconds via camera movement, crop shifts,
  callouts, text emphasis, source inserts, or micro-beats.
- Camera moves must have editorial intent: target a detail, reveal context, create emphasis, or
  maintain motion continuity into the next cut. Avoid constant random drifting.
- Use cut_bias='visual_lead' for a J-cut feel (new visual arrives before the narration boundary) or
  cut_bias='audio_lead' for an L-cut feel (old visual trails under the next narration phrase). Keep
  cut_offset_seconds subtle, usually 0.08-0.35 seconds.
- Use transition_out selectively. Match cuts should preserve a shape/position; smash cuts are rare;
  cross dissolves are for softer time/context changes; whip pans are for energetic motion continuity.
- Add restrained audio_cues on meaningful edits: whoosh for motion, impact/braam for reveals,
  click/ding for UI/stat moments, glitch/static for LobbySignal digital breaks, and riser before a
  reveal. Do not put a sound on every cut.
Effects are optional and must be used selectively. For stat_count_up, final_value must equal the
verified number from research and verified_value must store that same verified number. Never invent
a verified_value. Keep meme_flash requested duration between 0.5 and 1.5 seconds."""

KERNELRUSH = """KernelRush V4 direction: premium technology documentary/editorial pacing.
Favor full-screen source interfaces, purposeful dolly/orbit/rack-focus camera work, depth-separated
UI, subtle 3D stages, clean match cuts, and quiet moments between denser information. The brand is
precise rather than flashy. Use whoosh/impact/click sound design sparingly. Plan approximately
15-25 semantic scenes, but create micro-beats inside scenes so a scene may contain multiple edits."""

LOBBYSIGNAL = """LobbySignal V4 direction: faster gaming/internet-culture editing with full-bleed
gameplay/source media, aggressive but controlled crop changes, whip/match/smash cuts, kinetic type,
split-screen comparisons, freeze-frame callouts, glitch accents, 3D graphic moments, and stronger
impact/glitch/riser sound design. Keep it legible and intentional rather than chaotic. Plan
approximately 20-35 semantic scenes and use micro-beats for sub-second-to-two-second visual changes."""


def _prompt(channel_id: str) -> str:
    if channel_id == "kernelrush":
        channel = KERNELRUSH
    elif channel_id == "lobbysignal":
        channel = LOBBYSIGNAL
    else:
        raise ValueError(f"unsupported channel: {channel_id}")

    vocabulary = (
        f"\nRegistered scene types: {sorted(SCENE_TYPES)}"
        f"\nRegistered motions: {sorted(MOTIONS)}"
        f"\nRegistered transitions: {sorted(TRANSITIONS)}"
        f"\nRegistered shot styles: {sorted(SHOT_STYLES)}"
        f"\nRegistered camera presets: {sorted(CAMERA_PRESETS)}"
        f"\nRegistered cut biases: {sorted(CUT_BIASES)}"
        f"\nRegistered effects: {sorted(EFFECT_KINDS)}"
        f"\nRegistered micro-beats: {sorted(MICRO_BEAT_KINDS)}"
        f"\nRegistered audio cues: {sorted(AUDIO_CUE_KINDS)}"
        f"\nRegistered transition_out values: {sorted(TRANSITION_OUTS)}"
    )
    return COMMON + "\n\n" + channel + vocabulary


def plan_longform_scenes(channel_id: str, script: str, packet: dict, llm) -> ScenePlan:
    payload = llm.generate_json(
        _prompt(channel_id),
        {
            "channel_id": channel_id,
            "format": "longform",
            "script": script,
            "research": packet,
        },
        repair_prompt=REPAIR_PROMPT,
    )
    return parse_scene_plan(payload)
