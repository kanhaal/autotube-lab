import pytest

from app.planning.shorts import build_short_script, plan_short_scenes
from app.shorts.pipeline import build_short_story


class FakeLLM:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def generate_json(self, prompt, payload, **kwargs):
        self.calls.append((prompt, payload, kwargs))
        return self.responses.pop(0)


def packet():
    return {
        "topic": "Alpha launch",
        "sources": [
            {
                "source_name": "A",
                "url": "https://a.example",
                "text": "Alpha launched a local developer tool in 2026 with offline processing.",
            },
            {
                "source_name": "B",
                "url": "https://b.example",
                "text": "The Alpha tool can process projects locally and was released in 2026.",
            },
        ],
    }


def short_script_words(count=82):
    words = ["Alpha", "launched", "a", "local", "developer", "tool", "with", "offline", "processing"]
    return " ".join((words * ((count // len(words)) + 1))[:count]) + "."


def short_plan(channel_id="kernelrush", count=6):
    scenes = []
    for index in range(count):
        scenes.append(
            {
                "id": f"short-{index + 1}",
                "narration": "Alpha launched a local developer tool.",
                "purpose": "short beat",
                "scene_type": "hook" if index == 0 else "headline",
                "headline": "ALPHA GOES LOCAL",
                "subheadline": "Offline processing",
                "source_ids": ["source_1"],
                "asset_ids": [],
                "motion": "punch_in" if index == 0 else "push_up",
                "emphasis": ["local"],
                "transition": "cut",
                "fallback_scene_type": "fallback_editorial",
                "data": {},
            }
        )
    return {
        "channel_id": channel_id,
        "format": "short",
        "scenes": scenes,
    }


def test_short_script_is_separate_bounded_and_evidence_only_prompted():
    script = short_script_words()
    llm = FakeLLM([{"script": script}])

    result = build_short_script(packet(), "Long-form approved story.", llm)

    assert result == script
    assert 70 <= len(result.split()) <= 115
    prompt, payload, kwargs = llm.calls[0]
    assert "30-45" in prompt
    assert "only" in prompt.lower()
    assert "supplied" in prompt.lower()
    assert payload["research"] == packet()
    assert payload["approved_long_script"] == "Long-form approved story."
    assert "repair_prompt" in kwargs


def test_short_script_rejects_out_of_bounds_word_count():
    llm = FakeLLM([{"script": "Too short for a real Short."}])

    with pytest.raises(ValueError, match="word count"):
        build_short_script(packet(), "Long-form approved story.", llm)


def test_short_scene_plan_is_vertical_specific_and_5_to_12_scenes():
    llm = FakeLLM([short_plan(count=6)])

    plan = plan_short_scenes("kernelrush", short_script_words(), packet(), llm)

    assert plan.format == "short"
    assert len(plan.scenes) == 6
    prompt, payload, _ = llm.calls[0]
    assert "5-12" in prompt
    assert "vertical" in prompt.lower()
    assert payload["format"] == "short"


def test_short_scene_plan_rejects_scene_count_outside_contract():
    llm = FakeLLM([short_plan(count=4)])

    with pytest.raises(ValueError, match="5-12"):
        plan_short_scenes("kernelrush", short_script_words(), packet(), llm)


def test_short_story_rechecks_fact_gate_before_returning():
    unsupported = short_script_words(80) + " 999 users joined."
    llm = FakeLLM([{"script": unsupported}, short_plan(count=6)])

    with pytest.raises(ValueError, match="fact validation"):
        build_short_story("kernelrush", packet(), "Long-form approved story.", llm)
