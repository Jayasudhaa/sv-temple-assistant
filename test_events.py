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
TIME_WORD_QUERIES = [
    "today",
    "tomorrow",
    "yesterday",
    "this week",
    "next week",
    "last week",
    "coming week",
    "upcoming week",
    "following week",
    "current week",
    "weekend",
    "next weekend",
    "this month",
    "next month",
    "this year",
    
]

@pytest.mark.parametrize("query", TIME_WORD_QUERIES)
def test_time_words_trigger_events(query):
    resp = answer_user(query, message_ts=NOW_TS)
    print(f"\nQUERY: {query}\n{resp}")
    assert_events_response(resp)

CALENDAR_WORD_QUERIES = [
    "events",
    "festival",
    "festivals",
    "schedule",
    "programs",
    "activities",
    "happening",
    "what's happening",
    "what is happening",
    "special events",
    "anything happening",
]

@pytest.mark.parametrize("query", CALENDAR_WORD_QUERIES)
def test_calendar_words_trigger_events(query):
    resp = answer_user(query, message_ts=NOW_TS)
    print(f"\nQUERY: {query}\n{resp}")
    assert_events_response(resp)

CONTACT_QUERIES = [
    "temple manager",
    "president",
    "secretary",
    "phone number",
    "contact temple",
]
import re

@pytest.mark.parametrize("query", CONTACT_QUERIES)
def assert_has_contact_info(resp: str):
    # must contain phone number or email
    has_phone = re.search(r"\d{3}[-.\s]?\d{3}[-.\s]?\d{4}", resp)
    has_email = "@" in resp

    assert has_phone or has_email

STORY_QUERIES = [
    "story of lord venkateswara",
    "significance of pongal",
    "why is ekadasi important",
]

@pytest.mark.parametrize("query", STORY_QUERIES)
def test_story_not_events(query):
    resp = answer_user(query, message_ts=NOW_TS)
    print(f"\nQUERY: {query}\n{resp}")
    assert "EVENTS" not in resp

SATYA_QUERIES = [
    "satyanarayana pooja",
    "satya narayana vratham",
    "when is satyanarayana",
]

@pytest.mark.parametrize("query", SATYA_QUERIES)
def test_satyanarayana_not_events(query):
    resp = answer_user(query, message_ts=NOW_TS)
    print(f"\nQUERY: {query}\n{resp}")
    assert "satyanarayana" in resp.lower()
    assert "EVENTS" not in resp

HOMAM_QUERIES = [
    "sudarshana homam",
    "homam schedule",
    "book homam",
]

@pytest.mark.parametrize("query", HOMAM_QUERIES)
def test_homam_not_events(query):
    resp = answer_user(query, message_ts=NOW_TS)
    print(f"\nQUERY: {query}\n{resp}")
    assert "homam" in resp.lower()
    assert "EVENTS" not in resp

ABHISHEKAM_QUERIES = [
    "venkateswara abhishekam",
    "siva abhishekam",
    "abhishekam sponsorship",
]

@pytest.mark.parametrize("query", ABHISHEKAM_QUERIES)
def test_abhishekam_not_events(query):
    resp = answer_user(query, message_ts=NOW_TS)
    print(f"\nQUERY: {query}\n{resp}")
    assert "abhishekam" in resp.lower()
    assert "EVENTS" not in resp

ARJITHA_QUERIES = [
    "arjitha seva",
    "book arjitha",
]

@pytest.mark.parametrize("query", ARJITHA_QUERIES)
def test_arjitha_not_events(query):
    resp = answer_user(query, message_ts=NOW_TS)
    print(f"\nQUERY: {query}\n{resp}")
    assert "arjitha" in resp.lower()
    assert "EVENTS" not in resp

PANCHANG_QUERIES = [
    "panchang today",
    "tithi today",
    "nakshatra today",
]

@pytest.mark.parametrize("query", PANCHANG_QUERIES)
def test_panchang_not_events(query):
    resp = answer_user(query, message_ts=NOW_TS)
    print(f"\nQUERY: {query}\n{resp}")
    assert "panchang" in resp.lower() or "tithi" in resp.lower()
    assert "EVENTS" not in resp

CULTURAL_QUERIES = [
    "dance program",
    "singing event",
    "bhajans",
    "cultural programs",
]

@pytest.mark.parametrize("query", CULTURAL_QUERIES)
def test_cultural_not_events(query):
    resp = answer_user(query, message_ts=NOW_TS)
    print(f"\nQUERY: {query}\n{resp}")
    assert "dance" in resp.lower() or "bhajan" in resp.lower() or "cultural" in resp.lower()
    assert "EVENTS" not in resp

VEDIC_QUERIES = [
    "sri suktham",
    "purusha suktham",
    "vishnu sahasranamam",
]

@pytest.mark.parametrize("query", VEDIC_QUERIES)
def test_vedic_not_events(query):
    resp = answer_user(query, message_ts=NOW_TS)
    print(f"\nQUERY: {query}\n{resp}")
    assert "suktham" in resp.lower() or "sahasranamam" in resp.lower()
    assert "EVENTS" not in resp

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
