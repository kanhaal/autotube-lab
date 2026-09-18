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
    assert scene.effects == ()
    assert scene.transition_out is None
    assert plan.schema_version == "1"


def test_scene_schema_accepts_additive_effects_and_transition_out():
    payload = base_payload()
    payload["scenes"][0]["effects"] = [
        {
            "kind": "auto_zoom",
            "target": {"x": 0.15, "y": 0.2, "width": 0.45, "height": 0.3},
            "scale": 1.2,
        },
        {"kind": "ticker_overlay", "text": "Rumor", "badge": "UNCONFIRMED"},
    ]
    payload["scenes"][0]["transition_out"] = "whoosh_zoom"

    scene = parse_scene_plan(payload).scenes[0]

    assert [effect["kind"] for effect in scene.effects] == ["auto_zoom", "ticker_overlay"]
    assert scene.transition_out == "whoosh_zoom"


def test_scene_schema_rejects_unknown_effect_and_transition_out():
    payload = base_payload()
    payload["scenes"][0]["effects"] = [{"kind": "not_real"}]
    try:
        parse_scene_plan(payload)
    except ValueError as exc:
        assert "effect" in str(exc)
    else:
        raise AssertionError("expected ValueError")

    payload = base_payload()
    payload["scenes"][0]["transition_out"] = "random_transition"
    try:
        parse_scene_plan(payload)
    except ValueError as exc:
        assert "transition_out" in str(exc)
    else:
        raise AssertionError("expected ValueError")



def test_scene_schema_accepts_v4_editorial_direction_fields():
    payload = base_payload()
    payload["scenes"][0]["shot_style"] = "source_full"
    payload["scenes"][0]["camera"] = {
        "preset": "dolly_in",
        "intensity": 0.8,
        "target": {"x": 0.62, "y": 0.36},
    }
    payload["scenes"][0]["micro_beats"] = [
        {"at": 0.7, "kind": "focus_punch"},
        {"at": 1.4, "kind": "callout"},
    ]
    payload["scenes"][0]["audio_cues"] = [
        {"at": 0.0, "kind": "whoosh", "volume": 0.18},
        {"at": 0.8, "kind": "impact", "volume": 0.12},
    ]
    payload["scenes"][0]["transition_out"] = "whip_pan"

    scene = parse_scene_plan(payload).scenes[0]

    assert scene.shot_style == "source_full"
    assert scene.camera["preset"] == "dolly_in"
    assert len(scene.micro_beats) == 2
    assert scene.audio_cues[0]["kind"] == "whoosh"
    assert scene.transition_out == "whip_pan"


def test_scene_schema_rejects_unknown_v4_editorial_values():
    payload = base_payload()
    payload["scenes"][0]["shot_style"] = "powerpoint_slide"
    try:
        parse_scene_plan(payload)
    except ValueError as exc:
        assert "shot_style" in str(exc)
    else:
        raise AssertionError("expected ValueError")

    payload = base_payload()
    payload["scenes"][0]["camera"] = {"preset": "random_camera"}
    try:
        parse_scene_plan(payload)
    except ValueError as exc:
        assert "camera" in str(exc)
    else:
        raise AssertionError("expected ValueError")

    payload = base_payload()
    payload["scenes"][0]["audio_cues"] = [{"at": 0, "kind": "airhorn"}]
    try:
        parse_scene_plan(payload)
    except ValueError as exc:
        assert "audio" in str(exc)
    else:
        raise AssertionError("expected ValueError")



def test_scene_schema_accepts_v4_cut_bias_and_lowpass_audio_cue():
    payload = base_payload()
    payload["scenes"][0]["cut_bias"] = "visual_lead"
    payload["scenes"][0]["cut_offset_seconds"] = 0.22
    payload["scenes"][0]["audio_cues"] = [
        {"at": 0.6, "kind": "lowpass", "duration": 0.7}
    ]

    scene = parse_scene_plan(payload).scenes[0]

    assert scene.cut_bias == "visual_lead"
    assert scene.cut_offset_seconds == 0.22
    assert scene.audio_cues[0]["kind"] == "lowpass"


def test_scene_schema_rejects_excessive_cut_offset():
    payload = base_payload()
    payload["scenes"][0]["cut_bias"] = "audio_lead"
    payload["scenes"][0]["cut_offset_seconds"] = 2.0

    try:
        parse_scene_plan(payload)
    except ValueError as exc:
        assert "cut_offset_seconds" in str(exc)
    else:
        raise AssertionError("expected ValueError")
