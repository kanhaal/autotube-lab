import pytest

from app.planning.scene_schema import parse_scene_plan


def valid_payload():
    return {
        "channel_id": "kernelrush",
        "format": "longform",
        "schema_version": "1",
        "scenes": [
            {
                "id": "s1",
                "narration": "Alpha launched a new tool.",
                "purpose": "hook",
                "scene_type": "hook",
                "headline": "Alpha launched",
                "subheadline": "",
                "source_ids": ["source_0"],
                "asset_ids": [],
                "motion": "slow_zoom",
                "emphasis": ["Alpha"],
                "transition": "cut",
                "fallback_scene_type": "fallback_editorial",
                "data": {},
            }
        ],
    }


def test_scene_plan_parses_source_ids_as_tuples():
    plan = parse_scene_plan(valid_payload())
    assert plan.scenes[0].source_ids == ("source_0",)


def test_scene_plan_rejects_unknown_scene_type():
    payload = valid_payload()
    payload["scenes"][0]["scene_type"] = "magic_ai_scene"
    with pytest.raises(ValueError, match="scene type"):
        parse_scene_plan(payload)


def test_scene_plan_rejects_duplicate_scene_ids():
    payload = valid_payload()
    payload["scenes"].append(dict(payload["scenes"][0]))
    with pytest.raises(ValueError, match="unique"):
        parse_scene_plan(payload)


def test_scene_plan_rejects_empty_narration():
    payload = valid_payload()
    payload["scenes"][0]["narration"] = ""
    with pytest.raises(ValueError, match="narration"):
        parse_scene_plan(payload)
