from app.editorial.director import build_editorial_bundle
from app.validation.facts import validate_script


class FakeLLM:
    def __init__(self, replies):
        self.replies = iter(replies)
        self.calls = 0

    def generate_json(self, *args, **kwargs):
        self.calls += 1
        return next(self.replies)


def outline_payload():
    return {
        "strongest_signal": "Alpha launched a local developer tool",
        "what_changed": "A new tool became available",
        "why_now": "It launched this week",
        "context": ["Alpha builds developer tools"],
        "evidence_order": ["source_0", "source_1"],
        "tension": "Local execution changes tradeoffs",
        "implication": "Developers gain another deployment option",
        "uncertainty": "Adoption is not known yet",
        "closing_takeaway": "Watch real usage next",
    }


def hooks_payload():
    return {
        "hooks": [
            {"text": "Alpha just changed local deployment.", "specificity": 9, "curiosity": 8, "clarity": 9, "brevity": 9, "fact_supported": True},
            {"text": "This developer tool is interesting.", "specificity": 5, "curiosity": 6, "clarity": 8, "brevity": 8, "fact_supported": True},
            {"text": "Alpha will replace the cloud.", "specificity": 9, "curiosity": 10, "clarity": 9, "brevity": 9, "fact_supported": False},
        ]
    }


def critique_payload(needs_rewrite):
    return {
        "needs_rewrite": needs_rewrite,
        "opening_strength": 8,
        "information_density": 8,
        "logical_flow": 8,
        "redundancy": 3,
        "factual_discipline": 9,
        "pacing": 8,
        "clarity": 9,
        "emotional_rhythm": 7,
        "payoff": 8,
        "notes": ["tighten the middle"] if needs_rewrite else [],
    }


def packet():
    return {
        "topic": "Alpha launches",
        "sources": [
            {"source_name": "Primary", "url": "https://a", "text": "Alpha launched a local developer tool this week."},
            {"source_name": "Secondary", "url": "https://b", "text": "The tool adds another deployment option for developers."},
        ],
    }


def test_director_rewrites_at_most_once_when_critic_requests_it():
    llm = FakeLLM([
        outline_payload(),
        hooks_payload(),
        {"script": "Alpha just changed local deployment. The tool adds another deployment option."},
        critique_payload(True),
        {"script": "Alpha just changed local deployment. The new local tool gives developers another deployment option."},
    ])

    bundle = build_editorial_bundle(packet(), llm)

    assert bundle.script.startswith("Alpha just changed local deployment")
    assert bundle.script != bundle.draft_script
    assert llm.calls == 5
    assert len(bundle.hooks) == 3


def test_director_skips_rewrite_when_critic_approves_draft():
    draft = "Alpha just changed local deployment. The tool adds another deployment option."
    llm = FakeLLM([
        outline_payload(),
        hooks_payload(),
        {"script": draft},
        critique_payload(False),
    ])

    bundle = build_editorial_bundle(packet(), llm)

    assert bundle.script == draft
    assert llm.calls == 4


def test_new_editorial_layer_does_not_bypass_fact_gate():
    llm = FakeLLM([
        outline_payload(),
        hooks_payload(),
        {"script": "Alpha gained 9,999 users today."},
        critique_payload(False),
    ])

    bundle = build_editorial_bundle(packet(), llm)
    result = validate_script(bundle.script, packet())

    assert not result.ok
    assert any("9,999" in reason for reason in result.reasons)
