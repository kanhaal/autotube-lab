from app.editorial.hooks import select_hook
from app.editorial.models import HookCandidate


def test_hook_selector_requires_exactly_three_candidates():
    try:
        select_hook((HookCandidate("a", 1, 1, 1, 1, True),))
    except ValueError as exc:
        assert "exactly three" in str(exc)
        return

    raise AssertionError("expected ValueError")


def test_hook_selector_rejects_unsupported_candidate_even_with_high_score():
    hooks = (
        HookCandidate("unsupported", 10, 10, 10, 10, False),
        HookCandidate("specific", 8, 8, 8, 8, True),
        HookCandidate("clear", 7, 7, 9, 7, True),
    )

    assert select_hook(hooks).text == "specific"


def test_hook_score_is_mean_of_numeric_dimensions():
    hook = HookCandidate("x", 8, 6, 10, 4, True)

    assert hook.score == 7
