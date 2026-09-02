"""Step 5: two reviewers either agree or produce a recorded disagreement."""

from __future__ import annotations

from compiled_ai.confirm import disagreements, kappa
from compiled_ai.model import Confirmation


def conf(digest: str, answer: bool | None, reviewer: str) -> Confirmation:
    return Confirmation(id=f"x.{digest}", sentence_digest=digest, reviewer=reviewer, answer=answer, provisional=False, allowed_example="a", forbidden_example="b")


def test_kappa_is_one_for_perfect_agreement_and_zero_for_chance() -> None:
    assert kappa([True, False, True, False], [True, False, True, False]) == 1.0
    assert abs(kappa([True, True, False, False], [True, False, True, False])) < 1e-9


def test_disagreements_are_listed_by_digest() -> None:
    a = [conf("d1", True, "ann"), conf("d2", False, "ann"), conf("d3", True, "ann")]
    b = [conf("d1", True, "bo"), conf("d2", True, "bo"), conf("d3", None, "bo")]
    assert disagreements(a, b) == [("d2", False, True), ("d3", True, None)]
