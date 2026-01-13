import pytest
from datetime import datetime
from zoneinfo import ZoneInfo

from backend.ask_temple import answer_user

# --------------------------------------------------
# TEST TIME (LOCKED)
# --------------------------------------------------
NOW_TS = int(datetime(2026, 1, 13, 12, 0, tzinfo=ZoneInfo("America/Denver")).timestamp())

# --------------------------------------------------
# EVENT QUERIES BY CATEGORY
# --------------------------------------------------

TODAY_QUERIES = [
    "events today",
    "today events",
    "what's happening today",
    "today's special",
]

TOMORROW_QUERIES = [
    "events tomorrow",
    "tomo events",
    "tomorrow's special",
    "what's happening tomorrow",
]

THIS_WEEK_QUERIES = [
    "events this week",
    "this week activities",
    "what's happening this week",
]

NEXT_WEEK_QUERIES = [
    "events next week",
    "next week activities",
    "what's happening next week",
]

NEXT_MONTH_QUERIES = [
    "events next month",
    "next month activities",
    "what's happening next month",
]

MONTH_QUERIES = [
    "events in january",
    "events in february",
    "events in march",
    "events in april",
    "events in may",
    "events in june",
    "events in july",
    "events in august",
    "events in september",
    "events in october",
    "events in november",
    "events in december",
]

# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def assert_events_response(resp: str):
    """Common checks for all EVENTS responses"""
    assert resp is not None
    assert isinstance(resp, str)
    assert resp.strip() != ""

    # Must be an EVENTS block
    assert "EVENTS" in resp

    # Must NOT silently fall back
    assert "I don’t have specific information" not in resp
    assert "I don't have specific information" not in resp


# --------------------------------------------------
# TESTS
# --------------------------------------------------

@pytest.mark.parametrize("query", TODAY_QUERIES)
def test_events_today(query):
    resp = answer_user(query, message_ts=NOW_TS)
    print(f"\nQUERY: {query}\n{resp}")
    assert_events_response(resp)
    assert "TODAY" in resp


@pytest.mark.parametrize("query", TOMORROW_QUERIES)
def test_events_tomorrow(query):
    resp = answer_user(query, message_ts=NOW_TS)
    print(f"\nQUERY: {query}\n{resp}")
    assert_events_response(resp)
    assert "TOMORROW" in resp


@pytest.mark.parametrize("query", THIS_WEEK_QUERIES)
def test_events_this_week(query):
    resp = answer_user(query, message_ts=NOW_TS)
    print(f"\nQUERY: {query}\n{resp}")
    assert_events_response(resp)
    assert "THIS WEEK" in resp or "WEEK" in resp


@pytest.mark.parametrize("query", NEXT_WEEK_QUERIES)
def test_events_next_week(query):
    resp = answer_user(query, message_ts=NOW_TS)
    print(f"\nQUERY: {query}\n{resp}")
    assert_events_response(resp)
    assert "NEXT WEEK" in resp


@pytest.mark.parametrize("query", NEXT_MONTH_QUERIES)
def test_events_next_month(query):
    resp = answer_user(query, message_ts=NOW_TS)
    print(f"\nQUERY: {query}\n{resp}")
    assert_events_response(resp)
    assert "EVENTS" in resp
    assert "MONTH" in resp or "FEBRUARY" in resp or "MARCH" in resp


@pytest.mark.parametrize("query", MONTH_QUERIES)
def test_events_by_month(query):
    resp = answer_user(query, message_ts=NOW_TS)
    print(f"\nQUERY: {query}\n{resp}")
    assert_events_response(resp)

    # Month name must appear
    month = query.split()[-1].upper()
    assert month[:3] in resp.upper()
