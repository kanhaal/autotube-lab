import pytest

from app.assets.resolver import AssetResolutionError, resolve_scene_assets
from app.planning.scene_schema import ScenePlan, SceneSpec


def packet():
    return {
        "sources": [
            {
                "source_name": "Official Alpha",
                "url": "https://example.com/alpha",
                "text": "Alpha launched.",
            },
            {
                "source_name": "Official Beta",
                "url": "https://example.com/beta",
                "text": "Beta confirmed the release.",
            },
        ]
    }


def test_source_browser_resolves_only_verified_research_url():
    scene = SceneSpec(
        id="s1",
        narration="Alpha launched.",
        purpose="show the official announcement",
        scene_type="source_browser",
        data={"source_url": "https://example.com/alpha"},
    )
    plan = ScenePlan(channel_id="kernelrush", format="longform", scenes=(scene,))

    requests = resolve_scene_assets(plan, packet())

    assert len(requests) == 1
    assert requests[0].id == "source-1"
    assert requests[0].kind == "source_screenshot"
    assert requests[0].source_url == "https://example.com/alpha"
    assert requests[0].source_name == "Official Alpha"
    assert requests[0].purpose == "show the official announcement"
    assert requests[0].required is False


def test_source_browser_rejects_url_not_in_research_packet():
    scene = SceneSpec(
        id="s1",
        narration="Something happened.",
        purpose="evidence",
        scene_type="source_browser",
        data={"source_url": "https://unverified.example/story"},
    )
    plan = ScenePlan(channel_id="kernelrush", format="longform", scenes=(scene,))

    with pytest.raises(AssetResolutionError, match="verified research source"):
        resolve_scene_assets(plan, packet())


def test_scene_without_external_asset_need_emits_no_requests():
    scene = SceneSpec(
        id="s1",
        narration="The number increased.",
        purpose="explain the statistic",
        scene_type="stat",
        data={"value": "42%"},
    )
    plan = ScenePlan(channel_id="kernelrush", format="longform", scenes=(scene,))

    assert resolve_scene_assets(plan, packet()) == ()
