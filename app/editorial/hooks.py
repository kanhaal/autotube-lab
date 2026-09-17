from __future__ import annotations

from app.editorial.models import HookCandidate


def select_hook(hooks: tuple[HookCandidate, ...]) -> HookCandidate:
    if len(hooks) != 3:
        raise ValueError("hook selection requires exactly three candidates")
    supported = [hook for hook in hooks if hook.fact_supported]
    if not supported:
        raise ValueError("at least one fact-supported hook is required")
    return max(supported, key=lambda hook: hook.score)
