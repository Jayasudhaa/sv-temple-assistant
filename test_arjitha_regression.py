import pytest
from datetime import datetime, date, time
from zoneinfo import ZoneInfo

from backend.ask_temple import answer_user

TZ = ZoneInfo("America/Denver")

# Stable reference date/time for deterministic outputs
REF_DATE = date(2026, 1, 23)


def ts(d: date, t: time) -> int:
    """Convert local date+time into epoch timestamp for message_ts."""
    return int(datetime(d.year, d.month, d.day, t.hour, t.minute, tzinfo=TZ).timestamp())


def assert_no_context_leakage(out: str):
    lowered = out.lower()
    forbidden = [
        "provided temple context",
        "does not contain",
        "not mentioned",
        "documents",
        "context does not",
        "based on the available information",
        "i cannot find",
        "not available in the provided context",
    ]
    for phrase in forbidden:
        assert phrase not in lowered, f"Context leakage phrase found: '{phrase}'\n\nOUT:\n{out}"


def assert_contains_any(out: str, must_contain_any):
    low = out.lower()
    assert any(x.lower() in low for x in must_contain_any), (
        f"Missing all expected markers: {must_contain_any}\n\nOUT:\n{out}"
    )


def assert_contains_all(out: str, must_contain_all):
    low = out.lower()
    for x in must_contain_all:
        assert x.lower() in low, f"Missing '{x}'\n\nOUT:\n{out}"


# ============================================================
# QUERY COVERAGE (REGRESSION)
# ============================================================

ARJITHA_CORE_QUERIES = [
    "arjitha",
    "arjita",
    "arjitha seva",
    "arjitha services",
    "arjitha seva list",
    "arjitha list",
    "private pooja",
    "private puja",
    "private pooja services",
    "private puja services",
    "home pooja",
    "home puja",
    "pooja at home",
    "puja at home",
    "pooja services offered",
    "puja services offered",
    "services offered",
    "seva list",
]

ARJITHA_MEANING_QUERIES = [
    "what is arjitha seva",
    "meaning of arjitha seva",
    "explain arjitha seva",
    "what is private pooja",
    "explain private puja",
    "meaning of private pooja services",
]

ARJITHA_BOOKING_QUERIES = [
    "how to book arjitha seva",
    "how do i book private puja",
    "how to schedule private pooja",
    "book home puja",
    "schedule home pooja",
    "how to arrange arjitha seva",
    "how to book pooja at home",
]

ARJITHA_LIST_QUERIES = [
    "list arjitha sevas available",
    "arjitha sevas available",
    "private pooja list",
    "available private pujas",
    "types of arjitha seva",
    "arjitha seva types",
    "what services are available at home",
    "what services are offered at temple",
]

ARJITHA_FEES_QUERIES = [
    "arjitha fee",
    "arjitha fees",
    "pooja fee list",
    "puja fee list",
    "private pooja fees",
    "private puja fees",
    "fees for home pooja",
    "fees for temple pooja",
    "sponsorship for private puja",
    "sponsorship amount for arjitha seva",
    "arjitha seva sponsorship",
    "arjitha seva price",
    "private pooja cost",
]

ARJITHA_CEREMONY_QUERIES = [
    "gruhapravesam at home",
    "gruhapravesam fee",
    "vaastu puja at home",
    "upanayanam at home",
    "upanayanam fee",
    "wedding at temple fee",
    "wedding at home fee",
    "seemantham at home",
    "namakaranam at home",
    "anna prasana fee",
    "aksharabhyasam fee",
    "last rites fee",
    "pinda pradanam with homam",
    "satyanarayana individual at home",
    "sudarsana homam fee",
    "varalakshmi vratham at home fee",
    "kalyanotsavam individual fee",
    "vastra samarpanam venkateswara sponsorship",
]

ARJITHA_PRIEST_SERVICE_QUERIES = [
    # NOTE: avoid singular keyword "priest" (your escalation block catches it)
    "priests for puja services",
    "priests for private puja services",
    "need priests for home puja",
    "arrange priests for gruhapravesam",
    "temple priests for home pooja",
]

ALL_ARJITHA_QUERIES = (
    ARJITHA_CORE_QUERIES
    + ARJITHA_MEANING_QUERIES
    + ARJITHA_BOOKING_QUERIES
    + ARJITHA_LIST_QUERIES
    + ARJITHA_FEES_QUERIES
    + ARJITHA_CEREMONY_QUERIES
    + ARJITHA_PRIEST_SERVICE_QUERIES
)

OFFICIAL_LINK = "https://svtempleco.org/Home/ArjithaSeva.html"


# ============================================================
# TESTS
# ============================================================

@pytest.mark.parametrize("q", ALL_ARJITHA_QUERIES)
def test_arjitha_all_queries_return_valid_arjitha_response(q):
    """
    Regression: Any query about Arjitha / Private Poojas must:
    - Return output
    - Not leak context phrases
    - Include the official link
    - Contain ARJITHA/PRIVATE POOJA marker (to ensure correct routing)
    - Not mistakenly return EVENTS/TEMPLE STATUS
    """
    out = answer_user(q, message_ts=ts(REF_DATE, time(11, 0)))

    assert out and out.strip(), f"Empty response for query: {q}"
    assert_no_context_leakage(out)

    # Must include official page link always (strong signal correct handler ran)
    assert OFFICIAL_LINK in out, f"Missing official link for query: {q}\n\nOUT:\n{out}"

    # Should look like Arjitha output, not calendar/events
    assert "📅 events" not in out.lower(), f"Incorrectly routed to EVENTS for query: {q}\n\nOUT:\n{out}"
    assert "temple status" not in out.lower(), f"Incorrectly routed to TEMPLE STATUS for query: {q}\n\nOUT:\n{out}"

    # Must contain "ARJITHA" or "PRIVATE POOJA"
    assert_contains_any(out, ["arjitha", "private pooja", "private puja"])

    # Should not show placeholders like Home: — / Temple: —
    low = out.lower()
    assert "home: —" not in low, f"Found Home placeholder dash for query: {q}\n\nOUT:\n{out}"
    assert "temple: —" not in low, f"Found Temple placeholder dash for query: {q}\n\nOUT:\n{out}"


@pytest.mark.parametrize("q", ARJITHA_MEANING_QUERIES)
def test_arjitha_meaning_queries(q):
    """
    Meaning/explain queries should return definition text
    """
    out = answer_user(q, message_ts=ts(REF_DATE, time(11, 5)))

    assert out and out.strip()
    assert_no_context_leakage(out)
    assert OFFICIAL_LINK in out

    assert_contains_all(out, [
        "ARJITHA SEVA",
        "special priest-performed service",
    ])


@pytest.mark.parametrize("q", ARJITHA_BOOKING_QUERIES)
def test_arjitha_booking_queries(q):
    """
    Booking queries should return booking steps
    """
    out = answer_user(q, message_ts=ts(REF_DATE, time(11, 10)))

    assert out and out.strip()
    assert_no_context_leakage(out)
    assert OFFICIAL_LINK in out

    assert_contains_any(out, ["HOW TO BOOK", "book", "schedule"])
    assert_contains_any(out, ["Contact temple"])


@pytest.mark.parametrize("q", ARJITHA_FEES_QUERIES + ARJITHA_LIST_QUERIES)
def test_arjitha_fee_or_list_queries_show_fee_list(q):
    """
    Fees/List queries should show the fee list format
    """
    out = answer_user(q, message_ts=ts(REF_DATE, time(11, 15)))

    assert out and out.strip()
    assert_no_context_leakage(out)
    assert OFFICIAL_LINK in out

    # Fee list markers
    assert_contains_any(out, [
        "Sponsorship Fee List",
        "PRIVATE POOJA FEES",
        "ARJITHA / PRIVATE POOJA",
    ])

    # Must mention sponsorship at least once
    assert "sponsorship" in out.lower(), f"Missing 'sponsorship' mention\n\nOUT:\n{out}"

    # Must contain at least one known service name
    assert_contains_any(out, [
        "Abhishekam",
        "Archana",
        "Gruhapravesam",
        "Upanayanam",
        "Wedding",
        "Seemantham",
    ])


@pytest.mark.parametrize("q", ARJITHA_CEREMONY_QUERIES)
def test_arjitha_specific_ceremony_queries_should_include_relevant_item(q):
    """
    Ceremony-specific queries should still route to Arjitha and
    include at least the ceremony keyword in output.
    """
    out = answer_user(q, message_ts=ts(REF_DATE, time(11, 20)))

    assert out and out.strip()
    assert_no_context_leakage(out)
    assert OFFICIAL_LINK in out

    lowq = q.lower()
    lowo = out.lower()

    # Expect the response to contain the ceremony concept
    # (we keep it soft to avoid brittle failures due to wording differences)
    key_markers = []
    if "gruhapravesam" in lowq:
        key_markers.append("gruhapravesam")
    if "upanayanam" in lowq:
        key_markers.append("upanayanam")
    if "wedding" in lowq:
        key_markers.append("wedding")
    if "seemantham" in lowq:
        key_markers.append("seemantham")
    if "namakaranam" in lowq:
        key_markers.append("naamakaranam")
    if "varalakshmi" in lowq:
        key_markers.append("varalakshmi")
    if "vastra" in lowq:
        key_markers.append("vastra")

    if key_markers:
        assert any(k in lowo for k in key_markers), (
            f"Expected at least one of {key_markers} in output\n\nOUT:\n{out}"
        )


@pytest.mark.parametrize("q", ARJITHA_PRIEST_SERVICE_QUERIES)
def test_arjitha_priest_services_queries_route_to_arjitha(q):
    """
    Priest-related private puja queries should route to Arjitha handler,
    not RAG fallback or escalation.
    """
    out = answer_user(q, message_ts=ts(REF_DATE, time(11, 25)))

    assert out and out.strip()
    assert_no_context_leakage(out)
    assert OFFICIAL_LINK in out

    assert_contains_any(out, ["arjitha", "private puja", "private pooja"])
    assert "📅 events" not in out.lower()
    assert "temple status" not in out.lower()
