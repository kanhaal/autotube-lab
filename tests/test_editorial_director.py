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
        "strongest_signal": "Alpha launched a local developer tool.",
        "what_changed": "The tool is now available.",
        "why_now": "The launch happened this week.",
        "context": ["Alpha builds developer software."],
        "evidence_order": ["primary", "secondary"],
        "tension": "Whether local execution changes deployment choices.",
        "implication": "Developers have another deployment option.",
        "uncertainty": "Adoption is not known yet.",
        "takeaway": "Watch actual developer usage.",
    }


def hooks_payload():
    return {
        "hooks": [
            {"text": "Alpha just changed where this tool can run.", "specificity": 9, "curiosity": 8, "clarity": 9, "brevity": 8, "fact_supported": True},
            {"text": "This launch matters more than it looks.", "specificity": 6, "curiosity": 8, "clarity": 7, "brevity": 9, "fact_supported": True},
            {"text": "Alpha will dominate the market.", "specificity": 8, "curiosity": 9, "clarity": 8, "brevity": 8, "fact_supported": False},
        ]
    }


def packet():
    return {
        "topic": "Alpha launch",
        "candidate": {"title": "Alpha launch", "summary": "Alpha released a local developer tool."},
        "sources": [
            {"source_name": "Primary", "url": "https://a", "text": "Alpha released a local developer tool this week."},
            {"source_name": "Secondary", "url": "https://b", "text": "Developers are discussing how local execution changes deployment choices."},
        ],
    }


def test_director_rewrites_once_when_critic_requests_it():
    llm = FakeLLM([
        outline_payload(),
        hooks_payload(),
        {"script": "Alpha released a local developer tool this week. Why it matters: deployment choices changed."},
        {"needs_rewrite": True, "issues": ["opening is flat"], "strengths": ["well sourced"]},
        {"script": "Alpha just changed where this tool can run. Alpha released a local developer tool this week. Why it matters: developers now have another deployment choice."},
    ])

    bundle = build_editorial_bundle(packet(), llm)

    assert llm.calls == 5
    assert bundle.script.startswith("Alpha just changed")
    assert bundle.draft_script != bundle.script
    assert bundle.chosen_hook.text == "Alpha just changed where this tool can run."


def test_director_skips_rewrite_when_critic_approves_draft():
    draft = "Alpha released a local developer tool this week. Why it matters: deployment choices changed."
    llm = FakeLLM([
        outline_payload(),
        hooks_payload(),
        {"script": draft},
        {"needs_rewrite": False, "issues": [], "strengths": ["clear"]},
    ])

    bundle = build_editorial_bundle(packet(), llm)

    assert llm.calls == 4
    assert bundle.script == draft


def test_director_output_still_fails_existing_fact_gate_for_unsupported_number():
    llm = FakeLLM([
        outline_payload(),
        hooks_payload(),
        {"script": "Alpha gained 9,999 users this week. Why it matters: adoption is accelerating."},
        {"needs_rewrite": False, "issues": [], "strengths": []},
    ])

    bundle = build_editorial_bundle(packet(), llm)

    assert not validate_script(bundle.script, packet()).ok
