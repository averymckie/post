"""Step 4: any altered quote is rejected; a fabricated deadline, actor, or role is rejected."""

from __future__ import annotations

from hypothesis import given
from hypothesis import strategies as st

from compiled_ai.check import check_proposal
from compiled_ai.model import Clock, Proposal, Sentence, sha256_text

TEXT = (
    "(i) determine within 20 days (excepting Saturdays, Sundays, and legal public holidays) after the "
    "receipt of any such request whether to comply with such request and shall immediately notify the "
    "person making such a request of –"
)
SENTENCE = Sentence(
    id="t:u0:s0", source_id="t", unit_id="u0", path="(a)(6)(A)(i)", start=0, end=len(TEXT), text=TEXT,
    origin_offset=0, page=1, digest=sha256_text(TEXT),
)
QUOTE = "determine within 20 days (excepting Saturdays, Sundays, and legal public holidays) after the receipt of any such request whether to comply with such request"
ROLES = ["agency", "head of the agency"]


def good() -> Proposal:
    return Proposal(
        kind="step", quote=QUOTE, actor="agency", subject="determination",
        clock=Clock(amount=20, unit="working_days", trigger="receipt", subject="determination"),
        allowed_example="a", forbidden_example="b",
    )


def reserved() -> Proposal:
    return Proposal(kind="reserved_decision", quote=QUOTE, actor="agency", role="agency", subject="whether to comply", allowed_example="a", forbidden_example="b")


def run(p: Proposal, siblings: tuple[Proposal, ...] = ()) -> tuple[bool, list[str]]:
    r = check_proposal(SENTENCE, p, siblings or (p,), {SENTENCE.digest: SENTENCE}, defined_terms=["agency"], roles=ROLES)
    return r.ok, [f.code for f in r.failures]


def test_good_proposal_with_shall_in_context_is_accepted() -> None:
    p = good()
    # the quote has no 'shall'; the sentence's own 'shall immediately notify' is not in the quote,
    # so a step needs the lead-in context. Without it: connective mismatch.
    ok, codes = run(p, (p, reserved()))
    assert not ok and codes == ["CONNECTIVE_MISMATCH"]
    p2 = p.model_copy(update={"quote": QUOTE + " and shall immediately notify the person making such a request of –"})
    ok, codes = run(p2, (p2, reserved()))
    assert ok, codes


@given(
    st.integers(min_value=0, max_value=len(QUOTE) - 1),
    st.sampled_from(["upper", "lower", "delete", "space", "swap", "ligature"]),
)
def test_any_altered_quote_is_rejected_unless_it_is_still_in_the_source(i: int, how: str) -> None:
    q = QUOTE
    if how == "upper":
        m = q[:i] + q[i].upper() + q[i + 1 :]
    elif how == "lower":
        m = q[:i] + q[i].lower() + q[i + 1 :]
    elif how == "delete":
        m = q[:i] + q[i + 1 :]
    elif how == "space":
        m = q[:i] + " " + q[i:]
    elif how == "swap":
        m = q[:i] + q[i + 1 : i + 2] + q[i : i + 1] + q[i + 2 :]
    else:
        m = q.replace("fi", "ﬁ") if "fi" in q else q[:i] + "ﬁ" + q[i:]
    p = good().model_copy(update={"quote": m})
    ok, codes = run(p, (p, reserved()))
    if m.encode() in TEXT.encode():
        assert "QUOTE_NOT_BYTE_EXACT" not in codes
    else:
        assert "QUOTE_NOT_BYTE_EXACT" in codes


def test_invented_deadline_is_rejected() -> None:
    p = good().model_copy(update={"clock": Clock(amount=30, unit="working_days", trigger="receipt", subject="determination")})
    ok, codes = run(p, (p, reserved()))
    assert "CLOCK_NOT_IN_QUOTE" in codes
    p = good().model_copy(update={"clock": Clock(amount=20, unit="months", trigger="receipt", subject="determination")})
    ok, codes = run(p, (p, reserved()))
    assert "CLOCK_NOT_IN_QUOTE" in codes


def test_undefined_actor_and_unnamed_role_are_rejected() -> None:
    p = good().model_copy(update={"actor": "the vendor"})
    assert "ACTOR_UNDEFINED" in run(p, (p, reserved()))[1]
    r = reserved().model_copy(update={"role": "the contractor"})
    assert "ROLE_UNDEFINED" in run(r)[1]


def test_decision_word_without_reserved_sibling_is_rejected() -> None:
    p = good().model_copy(update={"quote": QUOTE + " and shall immediately notify the person making such a request of –"})
    ok, codes = run(p, (p,))
    assert "ROLE_NOT_RESERVED" in codes


def test_examples_are_required_for_rule_statements() -> None:
    p = good().model_copy(update={"allowed_example": None})
    assert "EXAMPLES_MISSING" in run(p, (p, reserved()))[1]
