from __future__ import annotations

from app.assets.service import prepare_assets
from app.editorial.director import build_editorial_bundle
from app.editorial.ollama import OllamaJsonClient
from app.planning.scene_planner import plan_longform_scenes


def prepare_editorial(packet: dict, channel_id: str, llm=None):
    client = llm or OllamaJsonClient()
    bundle = build_editorial_bundle(packet, client)
    scene_plan = plan_longform_scenes(channel_id, bundle.script, packet, client)
    return bundle, scene_plan


def prepare_episode_assets(
    scene_plan,
    packet: dict,
    channel_cfg: dict,
    episode_dir,
    capturer=None,
):
    return prepare_assets(scene_plan, packet, channel_cfg, episode_dir, capturer)
