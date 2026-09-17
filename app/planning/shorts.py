from __future__ import annotations

from app.planning.scene_schema import ScenePlan, parse_scene_plan

SHORT_MIN_WORDS = 70
SHORT_MAX_WORDS = 115
SHORT_MIN_SCENES = 5
SHORT_MAX_SCENES = 12

REPAIR_PROMPT = (
    "Return only one valid JSON object matching the requested schema. "
    "Do not add commentary or markdown fences."
)

SHORT_SCRIPT_PROMPT = """Write a separate spoken 30-45 second YouTube Short from the supplied
verified research packet and approved long-form story. Use ONLY the supplied evidence. Do not
introduce new facts, dates, numbers, quotes, capabilities, causes, outcomes, or certainty. Open
with an aggressive but truthful first-second hook, move immediately through the strongest facts,
and end with a concise payoff. Target 70-115 spoken words. Return JSON with one key: script."""

SHORT_SCENE_PROMPT = """Plan a native vertical 1080x1920 YouTube Short from the supplied factual
Short script and research packet. Create 5-12 semantic scenes with a strong first-second hook,
mobile-safe typography, fast but readable pacing, and vertical-specific layouts. Do not crop or
reuse the long-form scene plan. Use ONLY facts and assets supported by the supplied script and
research. Return one JSON object with channel_id, format='short', and scenes. Every scene needs:
id, narration, purpose, scene_type, headline, subheadline, source_ids, asset_ids, motion, emphasis,
transition, fallback_scene_type, and data."""


def build_short_script(packet: dict, long_script: str, llm) -> str:
    payload = llm.generate_json(
        SHORT_SCRIPT_PROMPT,
        {"research": packet, "approved_long_script": long_script},
        repair_prompt=REPAIR_PROMPT,
    )
    script = str(payload.get("script", "")).strip()
    word_count = len(script.split())
    if not SHORT_MIN_WORDS <= word_count <= SHORT_MAX_WORDS:
        raise ValueError(
            f"Short script word count must be {SHORT_MIN_WORDS}-{SHORT_MAX_WORDS}; got {word_count}"
        )
    return script


def plan_short_scenes(channel_id: str, short_script: str, packet: dict, llm) -> ScenePlan:
    payload = llm.generate_json(
        SHORT_SCENE_PROMPT,
        {
            "channel_id": channel_id,
            "format": "short",
            "script": short_script,
            "research": packet,
        },
        repair_prompt=REPAIR_PROMPT,
    )
    plan = parse_scene_plan(payload)
    count = len(plan.scenes)
    if not SHORT_MIN_SCENES <= count <= SHORT_MAX_SCENES:
        raise ValueError(
            f"Short scene plan must contain {SHORT_MIN_SCENES}-{SHORT_MAX_SCENES} scenes; got {count}"
        )
    if plan.format != "short":
        raise ValueError("Short scene plan format must be 'short'")
    return plan
