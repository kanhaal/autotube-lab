from app.planning.scene_planner import plan_longform_scenes


class FakeLLM:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def generate_json(self, prompt, payload, **kwargs):
        self.calls.append((prompt, payload, kwargs))
        return self.response


def valid_plan(channel_id):
    return {
        "channel_id": channel_id,
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


def packet():
    return {
        "topic": "Alpha launch",
        "sources": [{"source_name": "A", "url": "https://a", "text": "Alpha launched."}],
    }


def test_kernelrush_scene_prompt_requests_premium_restrained_direction():
    llm = FakeLLM(valid_plan("kernelrush"))

    plan = plan_longform_scenes("kernelrush", "Alpha launched.", packet(), llm)

    prompt = llm.calls[0][0].lower()
    assert "15-25" in prompt
    assert "premium" in prompt
    assert "restrained" in prompt
    assert plan.channel_id == "kernelrush"


def test_lobbysignal_scene_prompt_requests_faster_gaming_direction():
    llm = FakeLLM(valid_plan("lobbysignal"))

    plan_longform_scenes("lobbysignal", "Alpha launched.", packet(), llm)

    prompt = llm.calls[0][0].lower()
    assert "20-35" in prompt
    assert "faster" in prompt
    assert "gaming" in prompt


def test_scene_planner_supplies_one_repair_prompt_to_structured_client():
    llm = FakeLLM(valid_plan("kernelrush"))

    plan_longform_scenes("kernelrush", "Alpha launched.", packet(), llm)

    assert len(llm.calls) == 1
    assert "repair_prompt" in llm.calls[0][2]
    assert "valid json" in llm.calls[0][2]["repair_prompt"].lower()
