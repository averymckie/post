"""Working days for FOIA clocks.

5 U.S.C. 552(a)(6)(A) counts days "excepting Saturdays, Sundays, and legal
public holidays". The legal public holidays are listed in 5 U.S.C. 6103(a),
and a holiday that falls on a Saturday is observed on the preceding Friday
and one that falls on a Sunday on the following Monday.

Provenance: the holiday list and the observance rules below are recorded as
data under the citation to 5 U.S.C. 6103. They were NOT verified against
fetched statute text in the build session (the source was unreachable; see
sources.yaml). Verify before relying on this module for a live deadline.

The rule for counting: the period starts on the day after the triggering
date, and each working day counts one. "Twenty working days after receipt"
on a Monday with no holidays is the Friday four weeks later minus... no:
it is the twentieth working day after that Monday, which is the Monday four
weeks later.
"""

from __future__ import annotations

from datetime import date, timedelta
from functools import lru_cache


def _nth_weekday(year: int, month: int, weekday: int, n: int) -> date:
    """The n-th (1-based) given weekday (Monday=0) of a month."""
    d = date(year, month, 1)
    offset = (weekday - d.weekday()) % 7
    return d + timedelta(days=offset + 7 * (n - 1))


def _last_weekday(year: int, month: int, weekday: int) -> date:
    d = date(year + (month == 12), (month % 12) + 1, 1) - timedelta(days=1)
    offset = (d.weekday() - weekday) % 7
    return d - timedelta(days=offset)


def _observed(d: date) -> date:
    if d.weekday() == 5:  # Saturday -> Friday
        return d - timedelta(days=1)
    if d.weekday() == 6:  # Sunday -> Monday
        return d + timedelta(days=1)
    return d


@lru_cache(maxsize=64)
def legal_public_holidays(year: int) -> frozenset[date]:
    """Legal public holidays as observed, per the list at 5 U.S.C. 6103(a)."""
    fixed = [
        date(year, 1, 1),  # New Year's Day
        date(year, 6, 19),  # Juneteenth National Independence Day
        date(year, 7, 4),  # Independence Day
        date(year, 11, 11),  # Veterans Day
        date(year, 12, 25),  # Christmas Day
    ]
    floating = [
        _nth_weekday(year, 1, 0, 3),  # Birthday of Martin Luther King, Jr.: third Monday in January
        _nth_weekday(year, 2, 0, 3),  # Washington's Birthday: third Monday in February
        _last_weekday(year, 5, 0),  # Memorial Day: last Monday in May
        _nth_weekday(year, 9, 0, 1),  # Labor Day: first Monday in September
        _nth_weekday(year, 10, 0, 2),  # Columbus Day: second Monday in October
        _nth_weekday(year, 11, 3, 4),  # Thanksgiving Day: fourth Thursday in November
    ]
    observed = {_observed(d) for d in fixed} | set(floating)
    # New Year's Day of the following year can be observed on December 31.
    nxt = _observed(date(year + 1, 1, 1))
    if nxt.year == year:
        observed.add(nxt)
    return frozenset(observed)


def is_working_day(d: date) -> bool:
    return d.weekday() < 5 and d not in legal_public_holidays(d.year)


def add_working_days(start: date, n: int) -> date:
    """The n-th working day after `start` (the start day itself is not counted)."""
    if n < 0:
        raise ValueError("n must be non-negative")
    d = start
    remaining = n
    while remaining > 0:
        d += timedelta(days=1)
        if is_working_day(d):
            remaining -= 1
    return d


def working_days_between(start: date, end: date) -> int:
    """Working days after `start` up to and including `end`; 0 if end <= start."""
    if end <= start:
        return 0
    count = 0
    d = start
    while d < end:
        d += timedelta(days=1)
        if is_working_day(d):
            count += 1
    return count
