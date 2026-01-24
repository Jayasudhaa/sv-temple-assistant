# tests/test_temple_hours_queries.py
import pytest
from datetime import datetime, date, time
from zoneinfo import ZoneInfo

from backend.ask_temple import answer_user

TZ = ZoneInfo("America/Denver")


# -------------------------------------------------
# Helpers
# -------------------------------------------------
def ts(d: date, t: time) -> int:
    """Create epoch timestamp in America/Denver for deterministic testing."""
    return int(datetime(d.year, d.month, d.day, t.hour, t.minute, t.second, tzinfo=TZ).timestamp())


FORBIDDEN_LEAK_PHRASES = [
    "provided temple context",
    "does not contain",
    "not mentioned",
    "documents",
    "context does not",
    "retrieved context",
    "from the context",
    "based on the context",
    "i couldn't find",
    "i cannot find",
]


def assert_no_context_leakage(out: str):
    lowered = out.lower()
    for phrase in FORBIDDEN_LEAK_PHRASES:
        assert phrase not in lowered, f"Context leakage phrase found: '{phrase}'\n\nOUT:\n{out}"


def assert_any(out: str, must_contain_any):
    low = out.lower()
    assert any(x.lower() in low for x in must_contain_any), (
        f"Expected any of {must_contain_any}\n\nOUT:\n{out}"
    )


def assert_all(out: str, must_contain_all):
    low = out.lower()
    for x in must_contain_all:
        assert x.lower() in low, f"Missing '{x}'\n\nOUT:\n{out}"


# -------------------------------------------------
# Reference Dates (2026)
# -------------------------------------------------
# Weekday reference: Fri Jan 23, 2026
WEEKDAY_REF_DATE = date(2026, 1, 23)

# Weekend reference: Sat Jan 24, 2026
WEEKEND_REF_DATE = date(2026, 1, 24)

# Holiday references (federal holidays)
# Jan 1, 2026  -> New Year's Day
# Jan 19, 2026 -> MLK Day (3rd Monday Jan 2026)
# Feb 16, 2026 -> Presidents Day (3rd Monday Feb 2026)
# May 25, 2026 -> Memorial Day (last Monday May 2026)
# Jul 4, 2026  -> Independence Day
# Sep 7, 2026  -> Labor Day (1st Monday Sep 2026)
# Nov 26, 2026 -> Thanksgiving (4th Thursday Nov 2026)
# Dec 25, 2026 -> Christmas
HOLIDAY_DATES = [
    ("new year", date(2026, 1, 1)),
    ("mlk", date(2026, 1, 19)),
    ("presidents", date(2026, 2, 16)),
    ("memorial", date(2026, 5, 25)),
    ("independence", date(2026, 7, 4)),
    ("labor", date(2026, 9, 7)),
    ("thanksgiving", date(2026, 11, 26)),
    ("christmas", date(2026, 12, 25)),
]


# -------------------------------------------------
# 1) Explicit Weekday/Weekend/Holiday Query Generators
# -------------------------------------------------
WEEKDAY_TOKENS = {
    "monday": ["monday", "mon", "mon."],
    "tuesday": ["tuesday", "tue", "tue.", "tues", "tues."],
    "wednesday": ["wednesday", "wed", "wed."],
    "thursday": ["thursday", "thu", "thu.", "thur", "thurs"],
    "friday": ["friday", "fri", "fri."],
}

WEEKEND_TOKENS = {
    "saturday": ["saturday", "sat", "sat."],
    "sunday": ["sunday", "sun", "sun."],
    "weekend": ["weekend", "weekends"],
}

HOLIDAY_TOKENS = [
    "holiday",
    "holidays",
    "federal holiday",
]

HOURS_KEYWORDS = [
    "hours",
    "timings",
    "timing",
    "open",
    "close",
    "time",
]


def generate_weekday_queries():
    """
    Generates ALL weekday queries:
    - mon/mon./monday + hours/timing/open/close/time
    - plus generic weekday hours queries
    """
    queries = []

    # Generic weekday phrasing
    generic_weekday_phrases = [
        "weekday hours",
        "weekdays hours",
        "weekday timing",
        "weekdays timing",
        "mon to fri hours",
        "monday to friday hours",
        "weekday temple hours",
    ]
    queries.extend(generic_weekday_phrases)

    # Day-specific weekday variants
    for _, tokens in WEEKDAY_TOKENS.items():
        for tok in tokens:
            for kw in HOURS_KEYWORDS:
                queries.append(f"{tok} {kw}")
                queries.append(f"{tok} temple {kw}")
                # Common user-style variants
                queries.append(f"{kw} on {tok}")
                queries.append(f"what are {tok} {kw}")

    # Deduplicate while preserving order
    seen = set()
    out = []
    for q in queries:
        qn = q.strip().lower()
        if qn not in seen:
            seen.add(qn)
            out.append(q)
    return out


def generate_weekend_queries():
    """
    Generates ALL weekend queries:
    - sat/sat./saturday + hours/timing/open/close/time
    - sun/sun./sunday + hours...
    - weekend/weekends + hours...
    - plus some common phrases
    """
    queries = []

    generic_weekend_phrases = [
        "weekend hours",
        "weekend temple hours",
        "weekend timings",
        "saturday hours",
        "sunday hours",
        "weekend open time",
        "weekend close time",
    ]
    queries.extend(generic_weekend_phrases)

    for _, tokens in WEEKEND_TOKENS.items():
        for tok in tokens:
            for kw in HOURS_KEYWORDS:
                queries.append(f"{tok} {kw}")
                queries.append(f"{tok} temple {kw}")
                queries.append(f"{kw} on {tok}")
                queries.append(f"what are {tok} {kw}")

    # Deduplicate while preserving order
    seen = set()
    out = []
    for q in queries:
        qn = q.strip().lower()
        if qn not in seen:
            seen.add(qn)
            out.append(q)
    return out


def generate_holiday_queries():
    """
    Generates ALL holiday queries:
    - holiday/holidays/federal holiday + hours/timing/open/close/time
    - plus specific holiday-name variants (new year, thanksgiving, etc.)
    """
    queries = []

    # Generic holiday phrasing
    for tok in HOLIDAY_TOKENS:
        for kw in HOURS_KEYWORDS:
            queries.append(f"{tok} {kw}")
            queries.append(f"{tok} temple {kw}")
            queries.append(f"{kw} on {tok}")

    # Specific holiday names (user might type these)
    holiday_name_variants = [
        "new year hours",
        "new year's day hours",
        "mlk day hours",
        "martin luther king day hours",
        "presidents day hours",
        "memorial day hours",
        "independence day hours",
        "july 4 hours",
        "labor day hours",
        "thanksgiving hours",
        "christmas hours",
    ]
    queries.extend(holiday_name_variants)

    # Deduplicate while preserving order
    seen = set()
    out = []
    for q in queries:
        qn = q.strip().lower()
        if qn not in seen:
            seen.add(qn)
            out.append(q)
    return out


ALL_WEEKDAY_QUERIES = generate_weekday_queries()
ALL_WEEKEND_QUERIES = generate_weekend_queries()
ALL_HOLIDAY_QUERIES = generate_holiday_queries()


# -------------------------------------------------
# 2) "Open now" correctness tests using real clock situations
# -------------------------------------------------
STATUS_CASES = [
    # WEEKDAY (Fri Jan 23, 2026)
    {
        "name": "weekday_open_morning",
        "query": "is temple open now",
        "message_ts": ts(WEEKDAY_REF_DATE, time(10, 0)),
        "expect_any": ["open", "open until", "temple status"],
        "expect_all": ["9:00", "12:00"],
    },
    {
        "name": "weekday_closed_midday_gap",
        "query": "temple hours now",
        "message_ts": ts(WEEKDAY_REF_DATE, time(13, 0)),
        "expect_any": ["closed now", "next opening"],
        "expect_all": ["9:00", "12:00", "6:00", "8:00"],
    },
    {
        "name": "weekday_open_evening",
        "query": "temple open now",
        "message_ts": ts(WEEKDAY_REF_DATE, time(19, 0)),
        "expect_any": ["open", "open until", "temple status"],
        "expect_all": ["6:00", "8:00"],
    },

    # WEEKEND (Sat Jan 24, 2026)
    {
        "name": "weekend_open_afternoon",
        "query": "is temple open now",
        "message_ts": ts(WEEKEND_REF_DATE, time(15, 0)),
        "expect_any": ["open", "open until", "temple status"],
        "expect_all": ["9:00", "8:00"],
    },
    {
        "name": "weekend_closed_late",
        "query": "is temple open now",
        "message_ts": ts(WEEKEND_REF_DATE, time(20, 30)),
        "expect_any": ["closed now", "next opening"],
        "expect_all": ["9:00", "8:00"],
    },

    # HOLIDAY (New Year Jan 1, 2026)
    {
        "name": "holiday_open",
        "query": "is temple open now",
        "message_ts": ts(date(2026, 1, 1), time(10, 0)),
        "expect_any": ["holiday", "open", "temple status"],
        "expect_all": ["9:00", "8:00"],
    },
    {
        "name": "holiday_closed_late",
        "query": "is temple open now",
        "message_ts": ts(date(2026, 1, 1), time(20, 30)),
        "expect_any": ["closed now", "next opening"],
        "expect_all": ["9:00", "8:00"],
    },
]


@pytest.mark.parametrize("case", STATUS_CASES, ids=[c["name"] for c in STATUS_CASES])
def test_temple_hours_status_open_closed(case):
    out = answer_user(case["query"], message_ts=case["message_ts"])

    assert out and out.strip(), f"Empty response for {case['name']}"
    assert_no_context_leakage(out)

    if "expect_any" in case:
        assert_any(out, case["expect_any"])
    if "expect_all" in case:
        assert_all(out, case["expect_all"])


# -------------------------------------------------
# 3) FULL COVERAGE: All Weekday Queries
# -------------------------------------------------
@pytest.mark.parametrize("q", ALL_WEEKDAY_QUERIES)
def test_all_weekday_queries(q):
    """
    For ALL weekday phrasing queries, we expect:
    - It returns something
    - No context leakage
    - Should look like weekday timings (9-12 and 6-8)
    """
    out = answer_user(q, message_ts=ts(WEEKDAY_REF_DATE, time(10, 0)))

    assert out and out.strip(), f"Empty response for weekday query: {q}"
    assert_no_context_leakage(out)

    # Must contain weekday time markers
    assert_all(out, ["9:00", "12:00"])
    # In weekday schedule mode, 6-8 should appear often; keep as "any" to avoid brittleness
    assert_any(out, ["6:00", "8:00", "6pm", "8pm"])


# -------------------------------------------------
# 4) FULL COVERAGE: All Weekend Queries
# -------------------------------------------------
@pytest.mark.parametrize("q", ALL_WEEKEND_QUERIES)
def test_all_weekend_queries(q):
    """
    For ALL weekend phrasing queries, we expect:
    - It returns something
    - No context leakage
    - Should show weekend timings (9-8)
    """
    out = answer_user(q, message_ts=ts(WEEKDAY_REF_DATE, time(10, 0)))  # query-based, not date-based

    assert out and out.strip(), f"Empty response for weekend query: {q}"
    assert_no_context_leakage(out)

    # Weekend schedule should have 9 to 8
    assert_all(out, ["9:00"])
    assert_any(out, ["8:00", "8 pm", "20:00"])


# -------------------------------------------------
# 5) FULL COVERAGE: All Holiday Queries
# -------------------------------------------------
@pytest.mark.parametrize("q", ALL_HOLIDAY_QUERIES)
def test_all_holiday_queries(q):
    """
    For ALL holiday phrasing queries, we expect:
    - It returns something
    - No context leakage
    - Should show holiday schedule (usually same as weekend: 9-8)
    """
    # Use a real holiday timestamp so your code goes into holiday logic
    out = answer_user(q, message_ts=ts(date(2026, 1, 1), time(10, 0)))

    assert out and out.strip(), f"Empty response for holiday query: {q}"
    assert_no_context_leakage(out)

    assert_all(out, ["9:00"])
    assert_any(out, ["8:00", "8 pm", "20:00", "holiday"])


# -------------------------------------------------
# 6) Verify Multiple Holiday Dates still behave like Holiday Hours
# -------------------------------------------------
@pytest.mark.parametrize("holiday_name, holiday_date", HOLIDAY_DATES)
def test_multiple_holiday_dates_hours(holiday_name, holiday_date):
    """
    Confirms that on real holiday calendar dates,
    asking temple hours shows 9-8 pattern.
    """
    out = answer_user("temple hours", message_ts=ts(holiday_date, time(10, 0)))

    assert out and out.strip(), f"Empty response for holiday date: {holiday_name} {holiday_date}"
    assert_no_context_leakage(out)

    assert_all(out, ["9:00"])
    assert_any(out, ["8:00", "holiday", "temple status"])
