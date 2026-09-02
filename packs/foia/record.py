"""The typed case record for a FOIA request.

Every field is something an agency's case file records. No field holds a
conclusion the statute reserves to a person: the record says whether a
foreseeable-harm finding was recorded, not whether harm is foreseeable. The
runtime evaluates the record as of `as_of`; it never reads the clock.

Exemption identifiers are the statute's own: "(b)(1)" through "(b)(9)".
"""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Notice(Strict):
    """A written notification to the person who made the request."""

    sent_on: date
    states_determination: bool = False
    states_reasons: bool = False
    states_liaison_assistance: bool = False
    states_appeal_right: bool = False
    appeal_period_days: int | None = Field(default=None, ge=0)
    states_dispute_resolution: bool = False
    states_judicial_review: bool = False
    names_and_titles_of_responsible_persons: tuple[str, ...] = ()


class Extension(Strict):
    """A written notice extending the time limits for unusual circumstances."""

    notice_sent_on: date
    states_unusual_circumstances: bool = False
    expected_dispatch_on: date | None = None
    extension_working_days: int = Field(ge=0)
    alternative_time_frame_agreed: bool = False


class Tolling(Strict):
    """One request by the agency to the requester for information."""

    information_requested_on: date
    response_received_on: date | None = None
    agency_finds_request_reasonable: bool | None = None


class Withholding(Strict):
    exemption: str
    exemption_conditions_found: bool | None = None
    harm_finding_recorded: bool | None = None
    prohibited_by_law: bool = False
    amount_deleted_indicated: bool = False
    indication_would_harm: bool | None = None


class Appeal(Strict):
    received_on: date
    determination: Literal["upheld", "upheld_in_part", "reversed", "pending"] = "pending"
    determination_on: date | None = None
    decided_by_head_of_agency: bool | None = None
    notice: Notice | None = None


class Record(Strict):
    as_of: date
    received_by_designated_component_on: date
    received_by_appropriate_component_on: date | None = None

    expedited_processing_requested: bool = False
    expedited_determination_on: date | None = None
    expedited_notice_on: date | None = None

    determination: Literal["comply", "deny", "partial", "pending"] = "pending"
    determination_on: date | None = None
    determination_notice: Notice | None = None
    records_made_available_on: date | None = None

    withholdings: tuple[Withholding, ...] = ()
    full_disclosure_possible: bool | None = None
    partial_disclosure_considered: bool | None = None
    segregability_review_recorded: bool | None = None

    extension: Extension | None = None
    tolling: tuple[Tolling, ...] = ()
    appeal: Appeal | None = None

    @property
    def adverse(self) -> bool:
        return self.determination in ("deny", "partial")
