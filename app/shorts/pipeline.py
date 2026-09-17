from __future__ import annotations

from dataclasses import dataclass

from app.planning.scene_schema import ScenePlan
from app.planning.shorts import build_short_script, plan_short_scenes
from app.validation.facts import validate_script


@dataclass(frozen=True)
class ShortStory:
    script: str
    scene_plan: ScenePlan


def build_short_story(channel_id: str, packet: dict, long_script: str, llm) -> ShortStory:
    script = build_short_script(packet, long_script, llm)
    validation = validate_script(script, packet)
    if not validation.ok:
        details = "; ".join(validation.reasons)
        raise ValueError(f"Short fact validation failed: {details}")
    scene_plan = plan_short_scenes(channel_id, script, packet, llm)
    return ShortStory(script=script, scene_plan=scene_plan)
