from __future__ import annotations

import wave
from pathlib import Path

from app.planning.scene_schema import ScenePlan, SceneSpec


def test_sound_design_materializes_scene_cues_at_editorial_timestamps(tmp_path: Path):
    from app.audio.sound_design import build_sound_design_events

    plan = ScenePlan(
        channel_id="kernelrush",
        format="longform",
        scenes=(
            SceneSpec(
                "s1",
                "One two three four.",
                "hook",
                "hook",
                audio_cues=(
                    {"at": 0.25, "kind": "whoosh", "volume": 0.18},
                    {"at": 0.75, "kind": "impact", "volume": 0.12},
                ),
            ),
            SceneSpec("s2", "Five six seven eight.", "evidence", "source_browser"),
        ),
    )

    events = build_sound_design_events(
        plan,
        duration_seconds=8.0,
        out_dir=tmp_path / "sound-design",
        channel_id="kernelrush",
    )

    assert [event.start_ms for event in events[:2]] == [250, 750]
    assert [event.volume for event in events[:2]] == [0.18, 0.12]
    assert all(event.path.is_file() for event in events)

    with wave.open(str(events[0].path), "rb") as wav:
        assert wav.getframerate() == 48000
        assert wav.getnchannels() == 1


def test_sound_design_adds_selective_transition_and_effect_hits(tmp_path: Path):
    from app.audio.sound_design import build_sound_design_events

    plan = ScenePlan(
        channel_id="lobbysignal",
        format="longform",
        scenes=(
            SceneSpec(
                "s1",
                "Fast gaming reveal.",
                "hook",
                "hook",
                transition_out="glitch_rgb_split",
                effects=({"kind": "stat_count_up", "final_value": 42, "verified_value": 42},),
            ),
            SceneSpec(
                "s2",
                "Second scene.",
                "evidence",
                "game_store",
                transition_out="smash_cut",
            ),
        ),
    )

    events = build_sound_design_events(
        plan,
        duration_seconds=6.0,
        out_dir=tmp_path / "sound-design",
        channel_id="lobbysignal",
    )

    names = [event.path.stem for event in events]
    assert any("glitch" in name for name in names)
    assert any("ding" in name for name in names)
    assert any("impact" in name for name in names)
    assert len(events) <= 12
