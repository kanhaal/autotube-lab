from __future__ import annotations

from app.planning.scene_schema import ScenePlan, SceneSpec


def _scene(index: int, *, scene_type: str = "headline", headline: str = "Headline", **kwargs):
    return SceneSpec(
        id=f"scene-{index}",
        narration=f"Narration {index}",
        purpose="explain",
        scene_type=scene_type,
        headline=headline,
        **kwargs,
    )


def _codes(issues) -> set[str]:
    return {issue.code for issue in issues}


def test_layout_rejects_missing_required_headline():
    from app.quality.layout import validate_scene_layout_metadata

    plan = ScenePlan(
        channel_id="kernelrush",
        format="longform",
        scenes=(_scene(1, scene_type="stat", headline=""),),
    )

    issues = validate_scene_layout_metadata(plan, "kernelrush")
    assert "empty_headline" in _codes(issues)


def test_layout_rejects_excessive_repeated_scene_type(monkeypatch):
    from app.quality import layout

    monkeypatch.setenv("AUTOTUBE_MAX_REPEAT_SCENE_TYPE", "2")
    plan = ScenePlan(
        channel_id="kernelrush",
        format="longform",
        scenes=tuple(_scene(index, scene_type="headline") for index in range(3)),
    )

    issues = layout.validate_scene_layout_metadata(plan, "kernelrush")
    assert "repeated_layout" in _codes(issues)


def test_layout_rejects_invalid_asset_id():
    from app.quality.layout import validate_scene_layout_metadata

    plan = ScenePlan(
        channel_id="kernelrush",
        format="longform",
        scenes=(_scene(1, asset_ids=("../unsafe.png",)),),
    )

    issues = validate_scene_layout_metadata(plan, "kernelrush")
    assert "invalid_asset_id" in _codes(issues)


def test_layout_rejects_caption_position_outside_normalized_safe_area():
    from app.quality.layout import validate_scene_layout_metadata

    plan = ScenePlan(
        channel_id="lobbysignal",
        format="short",
        scenes=(_scene(1, data={"caption_position": {"x": 0.5, "y": 1.1}}),),
    )

    issues = validate_scene_layout_metadata(plan, "lobbysignal")
    assert "caption_outside_safe_area" in _codes(issues)


def test_layout_accepts_varied_valid_plan():
    from app.quality.layout import validate_scene_layout_metadata

    plan = ScenePlan(
        channel_id="kernelrush",
        format="longform",
        scenes=(
            _scene(1, scene_type="hook"),
            _scene(2, scene_type="source_browser", asset_ids=("source-2",)),
            _scene(3, scene_type="comparison", data={"caption_position": {"x": 0.5, "y": 0.82}}),
        ),
    )

    assert validate_scene_layout_metadata(plan, "kernelrush") == ()
