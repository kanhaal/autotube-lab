from __future__ import annotations

from app.editorial.hooks import select_hook
from app.editorial.models import Critique, EditorialBundle, EditorialOutline, HookCandidate


OUTLINE_PROMPT = """You are the story architect for a factual YouTube explainer. Use only the supplied research packet. Return JSON only with strongest_signal, what_changed, why_now, context, evidence_order, tension, implication, uncertainty, closing_takeaway. Preserve uncertainty. Do not invent dates, numbers, quotes, causality, or capabilities."""

HOOK_PROMPT = """You are a hook editor. Use only the supplied evidence and outline. Return JSON only with exactly three hooks. Each hook object must contain text, specificity, curiosity, clarity, brevity, fact_supported. Scores are 0-10. Reject dishonest clickbait, unsupported certainty, invented numbers, dates, quotes, causality, or capabilities."""

SCRIPT_PROMPT = """You are writing a high-retention spoken YouTube script from verified research. Use only supplied evidence. Return JSON only with a single key: script. Use the selected hook first, then immediate context, 3-5 clear sections, a section literally titled 'Why it matters', and a tight close. Target about 650-1000 spoken words for production. No generic intro, no like/subscribe filler, no fabricated facts."""

CRITIC_PROMPT = """You are a strict editorial critic. Evaluate the draft only against the supplied verified evidence. Return JSON only with needs_rewrite, opening_strength, information_density, logical_flow, redundancy, factual_discipline, pacing, clarity, emotional_rhythm, payoff, notes. Numeric scores are 0-10. Set needs_rewrite true only for a material improvement, not stylistic preference."""

REWRITE_PROMPT = """Rewrite the supplied draft once using the critic notes while preserving every factual constraint from the research packet. Return JSON only with a single key: script. Do not add new claims, numbers, dates, quotes, causality, or capabilities."""

JSON_REPAIR_PROMPT = """Return only valid JSON matching the requested keys. Do not change factual content, add claims, or explain the repair."""


def _outline(data: dict) -> EditorialOutline:
    return EditorialOutline(
        strongest_signal=str(data["strongest_signal"]),
        what_changed=str(data["what_changed"]),
        why_now=str(data["why_now"]),
        context=tuple(str(x) for x in data.get("context", [])),
        evidence_order=tuple(str(x) for x in data.get("evidence_order", [])),
        tension=str(data.get("tension", "")),
        implication=str(data.get("implication", "")),
        uncertainty=str(data.get("uncertainty", "")),
        closing_takeaway=str(data.get("closing_takeaway", "")),
    )


def _hooks(data: dict) -> tuple[HookCandidate, HookCandidate, HookCandidate]:
    rows = data.get("hooks", [])
    if len(rows) != 3:
        raise ValueError("hook lab must return exactly three hooks")
    parsed = tuple(
        HookCandidate(
            text=str(row["text"]),
            specificity=float(row["specificity"]),
            curiosity=float(row["curiosity"]),
            clarity=float(row["clarity"]),
            brevity=float(row["brevity"]),
            fact_supported=bool(row["fact_supported"]),
        )
        for row in rows
    )
    return parsed  # type: ignore[return-value]


def _critique(data: dict) -> Critique:
    return Critique(
        needs_rewrite=bool(data["needs_rewrite"]),
        opening_strength=float(data["opening_strength"]),
        information_density=float(data["information_density"]),
        logical_flow=float(data["logical_flow"]),
        redundancy=float(data["redundancy"]),
        factual_discipline=float(data["factual_discipline"]),
        pacing=float(data["pacing"]),
        clarity=float(data["clarity"]),
        emotional_rhythm=float(data["emotional_rhythm"]),
        payoff=float(data["payoff"]),
        notes=tuple(str(x) for x in data.get("notes", [])),
    )


def build_editorial_bundle(packet: dict, llm) -> EditorialBundle:
    outline = _outline(
        llm.generate_json(
            OUTLINE_PROMPT,
            {"research": packet},
            repair_prompt=JSON_REPAIR_PROMPT,
        )
    )
    hooks = _hooks(
        llm.generate_json(
            HOOK_PROMPT,
            {"research": packet, "outline": outline.__dict__},
            repair_prompt=JSON_REPAIR_PROMPT,
        )
    )
    selected = select_hook(hooks)
    draft_payload = llm.generate_json(
        SCRIPT_PROMPT,
        {
            "research": packet,
            "outline": outline.__dict__,
            "selected_hook": selected.text,
        },
        repair_prompt=JSON_REPAIR_PROMPT,
    )
    draft = str(draft_payload["script"]).strip()
    critique = _critique(
        llm.generate_json(
            CRITIC_PROMPT,
            {"research": packet, "script": draft},
            repair_prompt=JSON_REPAIR_PROMPT,
        )
    )
    script = draft
    if critique.needs_rewrite:
        rewrite_payload = llm.generate_json(
            REWRITE_PROMPT,
            {
                "research": packet,
                "draft": draft,
                "critic_notes": list(critique.notes),
                "selected_hook": selected.text,
            },
            repair_prompt=JSON_REPAIR_PROMPT,
        )
        script = str(rewrite_payload["script"]).strip()
    return EditorialBundle(outline, hooks, selected, draft, critique, script)
