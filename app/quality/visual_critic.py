from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

_ALLOWED_CODES = {
    "clutter",
    "hierarchy",
    "repetition",
    "branding",
    "thumbnail_legibility",
}


@dataclass(frozen=True)
class VisualIssue:
    code: str
    message: str


@dataclass(frozen=True)
class VisualCritique:
    ok: bool
    issues: tuple[VisualIssue, ...]
    targeted_changes: tuple[str, ...]


def critique_contact_sheet(
    channel_id: str,
    contact_sheet: Path,
    thumbnails: tuple[Path, ...] | list[Path],
    llm,
) -> VisualCritique:
    contact = Path(contact_sheet)
    if not contact.is_file():
        raise FileNotFoundError(contact)
    thumb_paths = tuple(Path(path) for path in thumbnails)
    payload = {
        "channel_id": channel_id,
        "contact_sheet_path": str(contact.resolve()),
        "thumbnail_paths": [str(path.resolve()) for path in thumb_paths if path.is_file()],
        "allowed_issue_codes": sorted(_ALLOWED_CODES),
    }
    system_prompt = (
        "You are an advisory visual QA critic for a rendered YouTube episode. "
        "Return JSON only with keys ok (boolean), issues (array of {code,message}), and "
        "targeted_changes (array of concise strings). Use only allowed_issue_codes. "
        "Judge clutter, hierarchy, repetition, branding consistency, and thumbnail legibility. "
        "Do not make factual/editorial claims and do not override deterministic QA."
    )
    raw = llm.generate_json(
        system_prompt,
        payload,
        repair_prompt=(
            "Return one valid JSON object with ok, issues, and targeted_changes only. "
            "Issue codes must come from the supplied allowed_issue_codes."
        ),
    )
    if not isinstance(raw.get("ok"), bool):
        raise ValueError("visual critic must return boolean ok")
    raw_issues = raw.get("issues")
    raw_changes = raw.get("targeted_changes")
    if not isinstance(raw_issues, list) or not isinstance(raw_changes, list):
        raise ValueError("visual critic must return issues and targeted_changes arrays")

    issues: list[VisualIssue] = []
    for item in raw_issues:
        if not isinstance(item, dict):
            raise ValueError("visual critic issue must be an object")
        code = str(item.get("code", "")).strip()
        message = str(item.get("message", "")).strip()
        if code not in _ALLOWED_CODES:
            raise ValueError(f"unsupported visual issue code: {code}")
        if not message:
            raise ValueError("visual critic issue message is required")
        issues.append(VisualIssue(code=code, message=message))

    changes = tuple(str(change).strip() for change in raw_changes if str(change).strip())
    return VisualCritique(ok=raw["ok"], issues=tuple(issues), targeted_changes=changes)
