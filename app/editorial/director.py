from __future__ import annotations

from app.editorial.hooks import select_hook
from app.editorial.models import (
    Critique,
    EditorialBundle,
    EditorialOutline,
    HookCandidate,
)

REPAIR_PROMPT = (
    "Return only one valid JSON object matching the requested schema. "
    "Do not add commentary or markdown fences."
)

OUTLINE_PROMPT = """You are the story architect for a factual YouTube explainer.
Use ONLY the supplied research packet. Preserve uncertainty. Never invent dates, numbers, quotes,
causality, capabilities, or outcomes. Return JSON with keys: strongest_signal, what_changed,
why_now, context (array), evidence_order (array), tension, implication, uncertainty, takeaway."""

HOOK_PROMPT = """Generate exactly three factual opening hooks for the supplied story.
Use ONLY supplied evidence. No dishonest clickbait or unsupported certainty. Return JSON with a
hooks array. Each item must contain text, specificity, curiosity, clarity, brevity, and
fact_supported. Scores are numbers from 0 to 10."""

SCRIPT_PROMPT = """Write a spoken 4-7 minute YouTube explainer from the supplied research,
outline, and chosen hook. Use ONLY supplied evidence. Never invent dates, numbers, quotes,
causality, capabilities, or outcomes. Preserve uncertainty. Avoid generic intros and filler.
Include a clear 'Why it matters' section. Return JSON with one key: script."""

CRITIC_PROMPT = """Act as a strict editorial critic. Use the supplied evidence as the authority.
Assess opening strength, information density, logical flow, redundancy, unsupported inference,
pacing, clarity, emotional rhythm, and payoff. Do not introduce new facts. Return JSON with
needs_rewrite (boolean), issues (array), and strengths (array)."""

REWRITE_PROMPT = """Rewrite the draft once to address the supplied critique.
Use ONLY the research evidence and chosen hook. Preserve all factual uncertainty. Never add new
numbers, dates, quotes, causality, capabilities, or outcomes. Return JSON with one key: script."""


def _outline(payload: dict) -> EditorialOutline:
    return EditorialOutline(
        strongest_signal=str(payload["strongest_signal"]),
        what_changed=str(payload["what_changed"]),
        why_now=str(payload["why_now"]),
        context=tuple(str(x) for x in payload.get("context", [])),
        evidence_order=tuple(str(x) for x in payload.get("evidence_order", [])),
        tension=str(payload["tension"]),
        implication=str(payload["implication"]),
        uncertainty=str(payload["uncertainty"]),
        takeaway=str(payload["takeaway"]),
    )


def _hooks(payload: dict) -> tuple[HookCandidate, ...]:
    items = payload.get("hooks")
    if not isinstance(items, list) or len(items) != 3:
        raise ValueError("hook lab must return exactly three candidates")
    return tuple(
        HookCandidate(
            text=str(item["text"]),
            specificity=float(item["specificity"]),
            curiosity=float(item["curiosity"]),
            clarity=float(item["clarity"]),
            brevity=float(item["brevity"]),
            fact_supported=bool(item["fact_supported"]),
        )
        for item in items
    )


def _critique(payload: dict) -> Critique:
    return Critique(
        needs_rewrite=bool(payload["needs_rewrite"]),
        issues=tuple(str(x) for x in payload.get("issues", [])),
        strengths=tuple(str(x) for x in payload.get("strengths", [])),
    )


def build_editorial_bundle(packet: dict, llm) -> EditorialBundle:
    outline = _outline(
        llm.generate_json(OUTLINE_PROMPT, packet, repair_prompt=REPAIR_PROMPT)
    )
    hooks = _hooks(
        llm.generate_json(
            HOOK_PROMPT,
            {"research": packet, "outline": outline.__dict__},
            repair_prompt=REPAIR_PROMPT,
        )
    )
    chosen = select_hook(hooks)

    draft_payload = llm.generate_json(
        SCRIPT_PROMPT,
        {
            "research": packet,
            "outline": outline.__dict__,
            "chosen_hook": chosen.__dict__,
        },
        repair_prompt=REPAIR_PROMPT,
    )
    draft = str(draft_payload["script"]).strip()

    critique = _critique(
        llm.generate_json(
            CRITIC_PROMPT,
            {"research": packet, "draft_script": draft},
            repair_prompt=REPAIR_PROMPT,
        )
    )

    script = draft
    if critique.needs_rewrite:
        rewrite = llm.generate_json(
            REWRITE_PROMPT,
            {
                "research": packet,
                "draft_script": draft,
                "critique": critique.__dict__,
                "chosen_hook": chosen.__dict__,
            },
            repair_prompt=REPAIR_PROMPT,
        )
        script = str(rewrite["script"]).strip()

    return EditorialBundle(
        outline=outline,
        hooks=hooks,
        chosen_hook=chosen,
        draft_script=draft,
        critique=critique,
        script=script,
    )
