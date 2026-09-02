"""Rule functions for the FOIA pack. One function per confirmed statement.

Each function takes the typed record and returns Ok (the rule applied and is
satisfied), Fail (the case tripped the clause; the message quotes the clause
and the remedy says what to add), RouteTo (the statute reserves this decision
to a role, and it is outstanding), or Skip (the rule does not apply to this
case). No function decides anything the statute reserves to a person.

Provenance: drafted by a language model in an interactive session against
the confirmed statements in checklist.yaml, read in full before being
committed. The build refuses any function here that does not name a
confirmed statement, and any confirmed rule statement without a function.
"""

from __future__ import annotations

from datetime import date, timedelta

from compiled_ai.registry import Fail, Ok, Outcome, RouteTo, Skip, rule

from .calendar import add_working_days, working_days_between
from .record import Record

VALID_EXEMPTIONS = tuple(f"(b)({n})" for n in range(1, 10))
ADVERSE = ("deny", "partial")


# ----------------------------------------------------------------- helpers


def clock_start(rec: Record) -> date:
    """(a)(6)(A): the period commences on receipt by the appropriate component,
    but in any event not later than ten days after receipt by a designated
    component."""
    appropriate = rec.received_by_appropriate_component_on or rec.received_by_designated_component_on
    latest_start = rec.received_by_designated_component_on + timedelta(days=10)
    return min(appropriate, latest_start)


def tolled_working_days(rec: Record) -> int:
    total = 0
    for t in rec.tolling:
        end = t.response_received_on or rec.as_of
        total += working_days_between(t.information_requested_on, end)
    return total


def determination_deadline(rec: Record) -> date:
    days = 20
    if rec.extension is not None:
        days += rec.extension.extension_working_days
    deadline = add_working_days(clock_start(rec), days)
    tolled = tolled_working_days(rec)
    if tolled:
        deadline = add_working_days(deadline, tolled)
    return deadline


# ------------------------------------------------------ (a)(6)(A)(i), (I), (II)


@rule(id="foia.determination_clock", statement="foia.determination_clock", kind="step")
def determination_clock(rec: Record) -> Outcome:
    deadline = determination_deadline(rec)
    if rec.determination_on is not None:
        if rec.determination_on <= deadline:
            return Ok()
        late = working_days_between(deadline, rec.determination_on)
        return Fail(
            code="DETERMINATION_LATE",
            message=f"the determination was made {late} working day(s) after the 20-day period (excepting Saturdays, Sundays, and legal public holidays) ended on {deadline.isoformat()}",
            remedy="record the extension notice or the tolling that moved the deadline, if any; otherwise the statutory time limit was missed",
        )
    if rec.as_of <= deadline:
        return Ok()
    return Fail(
        code="DETERMINATION_OVERDUE",
        message=f"no determination has been made and the 20-day period ended on {deadline.isoformat()}",
        remedy="determine whether to comply with the request and notify the person who made it",
    )


@rule(id="foia.comply_reserved", statement="foia.comply_reserved", kind="reserved_decision")
def comply_reserved(rec: Record) -> Outcome:
    if rec.determination == "pending":
        return RouteTo(decision="whether to comply with the request", role="agency")
    return Ok()


@rule(id="foia.notice_immediate", statement="foia.notice_immediate", kind="step")
def notice_immediate(rec: Record) -> Outcome:
    if rec.determination == "pending":
        return Skip()
    n = rec.determination_notice
    if n is None:
        return Fail(
            code="NOTICE_MISSING",
            message="a determination was made but the record shows no notice to the person making the request",
            remedy="immediately notify the person making the request of the determination",
        )
    if rec.determination_on is not None and n.sent_on < rec.determination_on:
        return Fail(
            code="NOTICE_BEFORE_DETERMINATION",
            message="the notice is dated before the determination it reports",
            remedy="correct the notice date or the determination date",
        )
    return Ok()


@rule(id="foia.notice_reasons", statement="foia.notice_reasons", kind="step")
def notice_reasons(rec: Record) -> Outcome:
    n = rec.determination_notice
    if n is None:
        return Skip()
    if n.states_determination and n.states_reasons:
        return Ok()
    return Fail(
        code="NOTICE_WITHOUT_REASONS",
        message="the notice does not state such determination and the reasons therefor",
        remedy="state the determination and the reasons for it in the notice",
    )


@rule(id="foia.notice_liaison", statement="foia.notice_liaison", kind="step")
def notice_liaison(rec: Record) -> Outcome:
    n = rec.determination_notice
    if n is None:
        return Skip()
    if n.states_liaison_assistance:
        return Ok()
    return Fail(
        code="NOTICE_WITHOUT_LIAISON",
        message="the notice does not state the right of such person to seek assistance from the FOIA Public Liaison of the agency",
        remedy="add the right to seek assistance from the FOIA Public Liaison to the notice",
    )


# ------------------------------------------------- (a)(6)(A)(i)(III), (aa), (bb)


@rule(id="foia.adverse_condition", statement="foia.adverse_condition", kind="condition")
def adverse_condition(rec: Record) -> Outcome:
    return Ok() if rec.determination in ADVERSE else Skip()


@rule(id="foia.adverse_notice_appeal", statement="foia.adverse_notice_appeal", kind="step")
def adverse_notice_appeal(rec: Record) -> Outcome:
    if rec.determination not in ADVERSE or rec.determination_notice is None:
        return Skip()
    n = rec.determination_notice
    if n.states_appeal_right and n.appeal_period_days is not None and n.appeal_period_days >= 90:
        return Ok()
    return Fail(
        code="ADVERSE_NOTICE_WITHOUT_APPEAL_RIGHT",
        message="the adverse notice does not state the right of such person to appeal to the head of the agency within a period that is not less than 90 days after the date of such adverse determination",
        remedy="state the right to appeal to the head of the agency and an appeal period of at least 90 days",
    )


@rule(id="foia.appeal_period_reserved", statement="foia.appeal_period_reserved", kind="reserved_decision")
def appeal_period_reserved(rec: Record) -> Outcome:
    if rec.determination not in ADVERSE or rec.determination_notice is None:
        return Skip()
    if rec.determination_notice.appeal_period_days is None:
        return RouteTo(decision="the appeal period", role="head of the agency")
    return Ok()


@rule(id="foia.adverse_notice_dispute", statement="foia.adverse_notice_dispute", kind="step")
def adverse_notice_dispute(rec: Record) -> Outcome:
    if rec.determination not in ADVERSE or rec.determination_notice is None:
        return Skip()
    if rec.determination_notice.states_dispute_resolution:
        return Ok()
    return Fail(
        code="ADVERSE_NOTICE_WITHOUT_DISPUTE_RESOLUTION",
        message="the adverse notice does not state the right of such person to seek dispute resolution services from the FOIA Public Liaison of the agency or the Office of Government Information Services",
        remedy="add the right to seek dispute resolution services to the notice",
    )


# ------------------------------------------------------------ (a)(6)(A)(ii)


@rule(id="foia.appeal_clock", statement="foia.appeal_clock", kind="step")
def appeal_clock(rec: Record) -> Outcome:
    a = rec.appeal
    if a is None:
        return Skip()
    deadline = add_working_days(a.received_on, 20)
    if a.determination_on is not None:
        if a.determination_on <= deadline:
            return Ok()
        return Fail(
            code="APPEAL_DETERMINATION_LATE",
            message=f"the appeal was determined after twenty days (excepting Saturdays, Sundays, and legal public holidays) after the receipt of such appeal; the period ended on {deadline.isoformat()}",
            remedy="record the extension that moved the deadline, if any; otherwise the statutory time limit was missed",
        )
    if rec.as_of <= deadline:
        return Ok()
    return Fail(
        code="APPEAL_DETERMINATION_OVERDUE",
        message=f"no determination on the appeal has been made and the twenty-day period ended on {deadline.isoformat()}",
        remedy="make a determination with respect to the appeal",
    )


@rule(id="foia.appeal_reserved", statement="foia.appeal_reserved", kind="reserved_decision")
def appeal_reserved(rec: Record) -> Outcome:
    a = rec.appeal
    if a is None:
        return Skip()
    if a.determination == "pending" or a.decided_by_head_of_agency is None:
        return RouteTo(decision="the determination on appeal", role="head of the agency")
    if a.decided_by_head_of_agency:
        return Ok()
    return Fail(
        code="APPEAL_NOT_DECIDED_BY_HEAD_OF_AGENCY",
        message="the appeal is to the head of the agency, and the record shows it was decided by someone else",
        remedy="have the head of the agency make the determination on the appeal",
    )


@rule(id="foia.appeal_upheld_notice", statement="foia.appeal_upheld_notice", kind="step")
def appeal_upheld_notice(rec: Record) -> Outcome:
    a = rec.appeal
    if a is None or a.determination not in ("upheld", "upheld_in_part"):
        return Skip()
    if a.notice is not None and a.notice.states_judicial_review:
        return Ok()
    return Fail(
        code="APPEAL_NOTICE_WITHOUT_JUDICIAL_REVIEW",
        message="the denial was in whole or in part upheld on appeal, and the person was not notified of the provisions for judicial review of that determination",
        remedy="notify the person of the provisions for judicial review under paragraph (4)",
    )


# ------------------------------------------------ (a)(6)(A) flush language, (I)


@rule(id="foia.clock_commencement", statement="foia.clock_commencement", kind="step")
def clock_commencement(rec: Record) -> Outcome:
    if (
        rec.received_by_appropriate_component_on is not None
        and rec.received_by_appropriate_component_on < rec.received_by_designated_component_on
    ):
        return Fail(
            code="RECEIPT_DATES_INCONSISTENT",
            message="the request is recorded as received by the appropriate component before any designated component received it",
            remedy="correct the receipt dates",
        )
    return Ok()


@rule(id="foia.tolling_limited", statement="foia.tolling_limited", kind="condition")
def tolling_limited(rec: Record) -> Outcome:
    if not rec.tolling:
        return Skip()
    for t in rec.tolling:
        if t.information_requested_on < rec.received_by_designated_component_on:
            return Fail(
                code="TOLLING_BEFORE_RECEIPT",
                message="a tolling request for information is dated before the request was received",
                remedy="correct the dates; the 20-day period shall not be tolled except as the statute provides",
            )
    return Ok()


@rule(id="foia.tolling_once", statement="foia.tolling_once", kind="condition")
def tolling_once(rec: Record) -> Outcome:
    if not rec.tolling:
        return Skip()
    if len(rec.tolling) <= 1:
        return Ok()
    return Fail(
        code="TOLLING_MORE_THAN_ONCE",
        message=f"the agency may make one request to the requester for information and toll the 20-day period; the record shows {len(rec.tolling)}",
        remedy="only the first request for information tolls the period",
    )


@rule(id="foia.tolling_reasonable_reserved", statement="foia.tolling_reasonable_reserved", kind="reserved_decision")
def tolling_reasonable_reserved(rec: Record) -> Outcome:
    if not rec.tolling:
        return Skip()
    for t in rec.tolling:
        if t.agency_finds_request_reasonable is None:
            return RouteTo(decision="whether the request for information was reasonable", role="agency")
        if t.agency_finds_request_reasonable is False:
            return Fail(
                code="TOLLING_ON_UNREASONABLE_REQUEST",
                message="the period is tolled only while awaiting information that the agency has reasonably requested, and the agency has not found this request reasonable",
                remedy="do not count this request as tolling the period",
            )
    return Ok()


# ------------------------------------------------------------- (a)(6)(B)(i)


@rule(id="foia.extension_notice_content", statement="foia.extension_notice_content", kind="condition")
def extension_notice_content(rec: Record) -> Outcome:
    e = rec.extension
    if e is None:
        return Skip()
    if e.states_unusual_circumstances and e.expected_dispatch_on is not None:
        return Ok()
    return Fail(
        code="EXTENSION_NOTICE_INCOMPLETE",
        message="the time limits may be extended only by written notice setting forth the unusual circumstances for such extension and the date on which a determination is expected to be dispatched",
        remedy="state the unusual circumstances and the expected dispatch date in the written notice",
    )


@rule(id="foia.extension_reserved", statement="foia.extension_reserved", kind="reserved_decision")
def extension_reserved(rec: Record) -> Outcome:
    return Ok() if rec.extension is not None else Skip()


@rule(id="foia.extension_limit", statement="foia.extension_limit", kind="step")
def extension_limit(rec: Record) -> Outcome:
    e = rec.extension
    if e is None:
        return Skip()
    if e.extension_working_days <= 10 or e.alternative_time_frame_agreed:
        return Ok()
    return Fail(
        code="EXTENSION_OVER_TEN_WORKING_DAYS",
        message=f"no such notice shall specify a date that would result in an extension for more than ten working days; this one extends by {e.extension_working_days}",
        remedy="limit the extension to ten working days, or record the alternative time frame arranged under clause (ii)",
    )


# ---------------------------------------------------------------- (a)(6)(C)(i)


@rule(id="foia.prompt_release", statement="foia.prompt_release", kind="step")
def prompt_release(rec: Record) -> Outcome:
    if rec.determination not in ("comply", "partial"):
        return Skip()
    if rec.records_made_available_on is None:
        return Fail(
            code="RECORDS_NOT_MADE_AVAILABLE",
            message="upon a determination to comply, the records shall be made promptly available, and the record shows no release",
            remedy="make the records available and record the date",
        )
    if rec.determination_on is not None and rec.records_made_available_on < rec.determination_on:
        return Fail(
            code="RELEASE_BEFORE_DETERMINATION",
            message="the records are recorded as released before the determination to comply",
            remedy="correct the release date or the determination date",
        )
    return Ok()


@rule(id="foia.denial_names", statement="foia.denial_names", kind="step")
def denial_names(rec: Record) -> Outcome:
    if rec.determination not in ADVERSE or rec.determination_notice is None:
        return Skip()
    if rec.determination_notice.names_and_titles_of_responsible_persons:
        return Ok()
    return Fail(
        code="DENIAL_WITHOUT_NAMES",
        message="the notification of denial does not set forth the names and titles or positions of each person responsible for the denial",
        remedy="list the name and title or position of each person responsible for the denial",
    )


# ---------------------------------------------------------- (a)(6)(E)(ii)(I)


@rule(id="foia.expedited_clock", statement="foia.expedited_clock", kind="step")
def expedited_clock(rec: Record) -> Outcome:
    if not rec.expedited_processing_requested:
        return Skip()
    deadline = rec.received_by_designated_component_on + timedelta(days=10)
    if rec.expedited_determination_on is not None:
        notice_on = rec.expedited_notice_on
        if rec.expedited_determination_on <= deadline and notice_on is not None and notice_on <= deadline:
            return Ok()
        return Fail(
            code="EXPEDITED_DETERMINATION_LATE",
            message=f"a determination of whether to provide expedited processing, and notice of it, are due within 10 days after the date of the request; the period ended on {deadline.isoformat()}",
            remedy="record the determination and the notice dates, or the deadline was missed",
        )
    if rec.as_of <= deadline:
        return Ok()
    return Fail(
        code="EXPEDITED_DETERMINATION_OVERDUE",
        message=f"no determination of whether to provide expedited processing has been made and the 10-day period ended on {deadline.isoformat()}",
        remedy="determine whether to provide expedited processing and notify the person making the request",
    )


@rule(id="foia.expedited_reserved", statement="foia.expedited_reserved", kind="reserved_decision")
def expedited_reserved(rec: Record) -> Outcome:
    if not rec.expedited_processing_requested:
        return Skip()
    if rec.expedited_determination_on is None:
        return RouteTo(decision="whether to provide expedited processing", role="agency")
    return Ok()


# --------------------------------------------------------------- (a)(8)(A)


@rule(id="foia.withhold_only_if", statement="foia.withhold_only_if", kind="condition")
def withhold_only_if(rec: Record) -> Outcome:
    if not rec.withholdings:
        return Skip()
    for w in rec.withholdings:
        if w.prohibited_by_law or w.harm_finding_recorded is True:
            continue
        return Fail(
            code="WITHHOLDING_WITHOUT_BASIS",
            message=f"information may be withheld only if the agency reasonably foresees that disclosure would harm an interest protected by an exemption or disclosure is prohibited by law; the withholding under {w.exemption} records neither",
            remedy="record the foreseeable-harm finding or the legal prohibition, or release the information",
        )
    return Ok()


@rule(id="foia.foreseeable_harm_condition", statement="foia.foreseeable_harm_condition", kind="condition")
def foreseeable_harm_condition(rec: Record) -> Outcome:
    if any(w.harm_finding_recorded is True for w in rec.withholdings):
        return Ok()
    return Skip()


@rule(id="foia.foreseeable_harm_reserved", statement="foia.foreseeable_harm_reserved", kind="reserved_decision")
def foreseeable_harm_reserved(rec: Record) -> Outcome:
    if not rec.withholdings:
        return Skip()
    if any(w.harm_finding_recorded is None and not w.prohibited_by_law for w in rec.withholdings):
        return RouteTo(decision="whether disclosure would harm an interest protected by an exemption", role="agency")
    return Ok()


@rule(id="foia.prohibited_by_law_condition", statement="foia.prohibited_by_law_condition", kind="condition")
def prohibited_by_law_condition(rec: Record) -> Outcome:
    if any(w.prohibited_by_law for w in rec.withholdings):
        return Ok()
    return Skip()


@rule(id="foia.partial_disclosure_considered", statement="foia.partial_disclosure_considered", kind="step")
def partial_disclosure_considered(rec: Record) -> Outcome:
    if rec.full_disclosure_possible is not False:
        return Skip()
    if rec.partial_disclosure_considered:
        return Ok()
    return Fail(
        code="PARTIAL_DISCLOSURE_NOT_CONSIDERED",
        message="whenever the agency determines that a full disclosure of a requested record is not possible it shall consider whether partial disclosure of information is possible; the record shows no such consideration",
        remedy="record whether partial disclosure was considered",
    )


@rule(id="foia.full_disclosure_reserved", statement="foia.full_disclosure_reserved", kind="reserved_decision")
def full_disclosure_reserved(rec: Record) -> Outcome:
    if not rec.withholdings:
        return Skip()
    if rec.full_disclosure_possible is None:
        return RouteTo(decision="whether full disclosure is possible", role="agency")
    return Ok()


@rule(id="foia.segregate_release", statement="foia.segregate_release", kind="step")
def segregate_release(rec: Record) -> Outcome:
    if not rec.withholdings:
        return Skip()
    if rec.segregability_review_recorded is True:
        return Ok()
    return Fail(
        code="SEGREGABILITY_REVIEW_MISSING",
        message="the agency shall take reasonable steps necessary to segregate and release nonexempt information; the record shows no segregability review",
        remedy="record the segregability review and release the nonexempt information",
    )


@rule(id="foia.segregation_steps_reserved", statement="foia.segregation_steps_reserved", kind="reserved_decision")
def segregation_steps_reserved(rec: Record) -> Outcome:
    if not rec.withholdings:
        return Skip()
    if rec.segregability_review_recorded is None:
        return RouteTo(decision="what steps to segregate and release nonexempt information are reasonable", role="agency")
    return Ok()


# ----------------------------------------------------------------------- (b)


@rule(id="foia.exemptions_closed_list", statement="foia.exemptions_closed_list", kind="condition")
def exemptions_closed_list(rec: Record) -> Outcome:
    if not rec.withholdings:
        return Skip()
    for w in rec.withholdings:
        if w.exemption not in VALID_EXEMPTIONS:
            return Fail(
                code="EXEMPTION_NOT_IN_LIST",
                message=f"this section does not apply only to the matters listed in (b)(1) through (b)(9); {w.exemption!r} is not one of them",
                remedy="cite one of the nine exemptions, or release the information",
            )
    return Ok()


def _cites(rec: Record, exemption: str) -> Outcome:
    return Ok() if any(w.exemption == exemption for w in rec.withholdings) else Skip()


@rule(id="foia.exemption_1", statement="foia.exemption_1", kind="condition")
def exemption_1(rec: Record) -> Outcome:
    return _cites(rec, "(b)(1)")


@rule(id="foia.exemption_2", statement="foia.exemption_2", kind="condition")
def exemption_2(rec: Record) -> Outcome:
    return _cites(rec, "(b)(2)")


@rule(id="foia.exemption_3", statement="foia.exemption_3", kind="condition")
def exemption_3(rec: Record) -> Outcome:
    return _cites(rec, "(b)(3)")


@rule(id="foia.exemption_4", statement="foia.exemption_4", kind="condition")
def exemption_4(rec: Record) -> Outcome:
    return _cites(rec, "(b)(4)")


@rule(id="foia.exemption_5", statement="foia.exemption_5", kind="condition")
def exemption_5(rec: Record) -> Outcome:
    return _cites(rec, "(b)(5)")


@rule(id="foia.exemption_6", statement="foia.exemption_6", kind="condition")
def exemption_6(rec: Record) -> Outcome:
    return _cites(rec, "(b)(6)")


@rule(id="foia.exemption_7", statement="foia.exemption_7", kind="condition")
def exemption_7(rec: Record) -> Outcome:
    return _cites(rec, "(b)(7)")


@rule(id="foia.exemption_7_reserved", statement="foia.exemption_7_reserved", kind="reserved_decision")
def exemption_7_reserved(rec: Record) -> Outcome:
    cited = [w for w in rec.withholdings if w.exemption == "(b)(7)"]
    if not cited:
        return Skip()
    if any(w.exemption_conditions_found is None for w in cited):
        return RouteTo(
            decision="whether production of law enforcement records could reasonably be expected to cause a harm listed in (b)(7)",
            role="agency",
        )
    if all(w.exemption_conditions_found for w in cited):
        return Ok()
    return Fail(
        code="EXEMPTION_7_CONDITIONS_NOT_FOUND",
        message="records compiled for law enforcement purposes are exempt only to the extent that production could reasonably be expected to cause a harm listed in (b)(7)(A) through (F); the agency found no such harm",
        remedy="release the records, or record the (b)(7) harm the agency reasonably expects",
    )


@rule(id="foia.exemption_8", statement="foia.exemption_8", kind="condition")
def exemption_8(rec: Record) -> Outcome:
    return _cites(rec, "(b)(8)")


@rule(id="foia.exemption_9", statement="foia.exemption_9", kind="condition")
def exemption_9(rec: Record) -> Outcome:
    return _cites(rec, "(b)(9)")


@rule(id="foia.segregable_provided", statement="foia.segregable_provided", kind="step")
def segregable_provided(rec: Record) -> Outcome:
    if not rec.withholdings:
        return Skip()
    if rec.determination == "deny" and rec.segregability_review_recorded is not True:
        return Fail(
            code="FULL_DENIAL_WITHOUT_SEGREGABILITY_REVIEW",
            message="any reasonably segregable portion of a record shall be provided after deletion of the exempt portions; the whole record was withheld with no segregability review",
            remedy="review the record for segregable portions and provide them, recording the review",
        )
    return Ok()


@rule(id="foia.segregable_reserved", statement="foia.segregable_reserved", kind="reserved_decision")
def segregable_reserved(rec: Record) -> Outcome:
    if not rec.withholdings:
        return Skip()
    if rec.segregability_review_recorded is None:
        return RouteTo(decision="which portions of a record are reasonably segregable", role="agency")
    return Ok()


@rule(id="foia.deletion_indicated", statement="foia.deletion_indicated", kind="step")
def deletion_indicated(rec: Record) -> Outcome:
    if rec.determination != "partial" or not rec.withholdings:
        return Skip()
    for w in rec.withholdings:
        if w.amount_deleted_indicated or w.indication_would_harm is True:
            continue
        return Fail(
            code="DELETION_NOT_INDICATED",
            message=f"the amount of information deleted, and the exemption under which the deletion is made, shall be indicated on the released portion of the record; the deletion under {w.exemption} is not indicated and no harm from indicating it is recorded",
            remedy="mark the amount deleted and the exemption on the released portion, or record why the indication would harm a protected interest",
        )
    return Ok()
