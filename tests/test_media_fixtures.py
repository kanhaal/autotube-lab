from __future__ import annotations

import json
from pathlib import Path


REQUIRED_SCENE_TYPES = {
    "stat",
    "chart",
    "timeline",
    "source_browser",
    "comparison",
    "fallback_editorial",
}


def test_fixed_media_stories_cover_required_scene_families_without_remote_urls():
    fixture_dir = Path("tests/fixtures/media")
    for name, channel_id in (
        ("kernelrush_story.json", "kernelrush"),
        ("lobbysignal_story.json", "lobbysignal"),
    ):
        path = fixture_dir / name
        payload = json.loads(path.read_text(encoding="utf-8"))
        serialized = json.dumps(payload).lower()
        scene_types = {
            scene["scene_type"]
            for format_name in ("long", "short")
            for scene in payload[format_name]["scenes"]
        }

        assert payload["channel_id"] == channel_id
        assert REQUIRED_SCENE_TYPES <= scene_types
        assert "http://" not in serialized
        assert "https://" not in serialized
        assert payload["long"]["captions"]
        assert payload["short"]["captions"]
        assert payload["audio"]["music_cue"]
        assert payload["audio"]["sfx_events"]


def test_fixed_media_stories_are_synthetic_and_include_local_source_visual_data():
    fixture_dir = Path("tests/fixtures/media")
    for path in fixture_dir.glob("*_story.json"):
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["synthetic"] is True
        assert payload["source_visual"]["kind"] == "generated_local"
        assert payload["source_visual"]["label"]
        assert payload["source_visual"]["body"]


def test_sample_short_scripts_match_production_word_count_contract():
    fixture_dir = Path("tests/fixtures/media")
    for path in fixture_dir.glob("*_story.json"):
        payload = json.loads(path.read_text(encoding="utf-8"))
        script = " ".join(scene["narration"] for scene in payload["short"]["scenes"])
        word_count = len(script.split())
        assert 70 <= word_count <= 115, f"{path.name} Short has {word_count} words"
