from app.planning.scene_schema import parse_scene_plan


def base_payload():
    return {
        "channel_id": "kernelrush",
        "format": "longform",
        "scenes": [
            {
                "id": "s1",
                "narration": "Alpha launched a local developer tool.",
                "purpose": "hook",
                "scene_type": "hook",
                "headline": "ALPHA GOES LOCAL",
                "subheadline": "",
                "source_ids": ["source_1"],
                "asset_ids": [],
                "motion": "slow_zoom",
                "emphasis": ["local"],
                "transition": "cut",
                "fallback_scene_type": "fallback_editorial",
                "data": {},
            }
        ],
    }


def test_scene_schema_rejects_unknown_scene_type():
    payload = base_payload()
    payload["scenes"][0]["scene_type"] = "random_ai_scene"
    try:
        parse_scene_plan(payload)
    except ValueError as exc:
        assert "scene_type" in str(exc)
        return
    raise AssertionError("expected ValueError")


def test_scene_schema_requires_unique_ids():
    payload = base_payload()
    payload["scenes"].append(dict(payload["scenes"][0]))
    try:
        parse_scene_plan(payload)
    except ValueError as exc:
        assert "unique" in str(exc)
        return
    raise AssertionError("expected ValueError")


def test_scene_schema_requires_narration():
    payload = base_payload()
    payload["scenes"][0]["narration"] = ""
    try:
        parse_scene_plan(payload)
    except ValueError as exc:
        assert "narration" in str(exc)
        return
    raise AssertionError("expected ValueError")


def test_scene_schema_normalizes_list_fields_to_tuples():
    plan = parse_scene_plan(base_payload())
    scene = plan.scenes[0]
    assert scene.source_ids == ("source_1",)
    assert scene.asset_ids == ()
    assert scene.emphasis == ("local",)
    assert plan.schema_version == "1"
