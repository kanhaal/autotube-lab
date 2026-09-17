import pytest

from app.editorial.hooks import select_hook
from app.editorial.models import HookCandidate


def test_hook_selector_requires_exactly_three_candidates():
    with pytest.raises(ValueError, match="exactly three"):
        select_hook((HookCandidate("a", 1, 1, 1, 1, True),))


def test_hook_selector_rejects_unsupported_candidate_even_with_high_score():
    hooks = (
        HookCandidate("unsupported", 10, 10, 10, 10, False),
        HookCandidate("specific", 8, 8, 8, 8, True),
        HookCandidate("clear", 7, 7, 9, 7, True),
    )
    assert select_hook(hooks).text == "specific"


def test_hook_selector_preserves_input_order_on_ties():
    hooks = (
        HookCandidate("first", 8, 8, 8, 8, True),
        HookCandidate("second", 8, 8, 8, 8, True),
        HookCandidate("third", 7, 7, 7, 7, True),
    )
    assert select_hook(hooks).text == "first"


def test_hook_selector_fails_if_no_hook_is_fact_supported():
    hooks = tuple(HookCandidate(str(i), 9, 9, 9, 9, False) for i in range(3))
    with pytest.raises(ValueError, match="fact-supported"):
        select_hook(hooks)
