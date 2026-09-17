from __future__ import annotations

from app.editorial.director import build_editorial_bundle
from app.editorial.ollama import OllamaJsonClient
from app.planning.scene_planner import plan_longform_scenes


def prepare_editorial(packet: dict, channel_id: str, llm=None):
    client = llm or OllamaJsonClient()
    bundle = build_editorial_bundle(packet, client)
    scene_plan = plan_longform_scenes(channel_id, bundle.script, packet, client)
    return bundle, scene_plan
