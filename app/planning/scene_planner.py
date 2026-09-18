from __future__ import annotations

from app.planning.scene_schema import (
    EFFECT_KINDS,
    MOTIONS,
    SCENE_TYPES,
    TRANSITIONS,
    TRANSITION_OUTS,
    ScenePlan,
    parse_scene_plan,
)

REPAIR_PROMPT = (
    "Return one valid JSON object matching the requested scene-plan schema. "
    "Use only the registered scene types, motions, transitions, effects, and transition_out values."
)

COMMON = """You are the visual director for a factual faceless YouTube explainer.
Use ONLY the supplied approved script and research packet. Do not invent visual facts, statistics,
quotes, products, interfaces, or source claims. Prefer source/browser/product cards and original
charts, comparisons, timelines, counters, diagrams, and typography over generic imagery.
Return JSON with channel_id, format='longform', and scenes. Each scene must contain id, narration,
purpose, scene_type, headline, subheadline, source_ids, asset_ids, motion, emphasis, transition,
fallback_scene_type, and data. Scenes MAY also contain an optional effects array and optional
transition_out. Effects are render instructions only and must never introduce claims that are not
already supported by the script/research. Use stat_count_up only for a verified numeric value.
Keep meme_flash requests between 0.5 and 1.5 seconds. Use kinetic_word_reveal only when word-level
caption timing is useful."""

KERNELRUSH = """KernelRush direction: premium technology/editorial atmosphere with restrained
motion, clean hierarchy, generous spacing, and smooth transitions. Plan approximately 15-25
semantic scenes for a normal 4-7 minute episode. Use faster cuts only in the opening hook."""

LOBBYSIGNAL = """LobbySignal direction: faster gaming and internet-culture editorial pacing with
kinetic typography, punchier emphasis, game/store/context cards, timelines, and counters. Plan
approximately 20-35 semantic scenes for a normal 4-7 minute episode without becoming chaotic."""


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
        f"\nRegistered optional effects: {sorted(EFFECT_KINDS)}"
        f"\nRegistered optional transition_out values: {sorted(TRANSITION_OUTS)}"
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
