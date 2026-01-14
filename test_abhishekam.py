import pytest
from datetime import datetime
from zoneinfo import ZoneInfo

from backend.ask_temple import answer_user

TZ = ZoneInfo("America/Denver")

# Fixed timestamp for deterministic output
NOW_TS = int(datetime(2026, 1, 5, 10, 0, tzinfo=TZ).timestamp())

# =========================================================
# ALL ABHISHEKAM QUERY VARIANTS (REAL USER LANGUAGE)
# =========================================================

ABHISHEKAM_QUERIES = [

    # -------------------------------------------------
    # GENERIC
    # -------------------------------------------------
    "abhishekam",
    "abhishekam schedule",
    "when is abhishekam",
    "temple abhishekam",
    "list abhishekams",

    # -------------------------------------------------
    # DEITY-SPECIFIC
    # -------------------------------------------------
    "siva abhishekam",
    "shiva abhishekam",
    "venkateswara abhishekam",
    "balaji abhishekam",
    "tirupati abhishekam",
    "andal abhishekam",
    "mahalakshmi abhishekam",
    "hanuman abhishekam",
    "murugan abhishekam",
    "ganapati abhishekam",
    "sai baba abhishekam",
    "raghavendra swamy abhishekam",

    # -------------------------------------------------
    # TIME-RELATIVE
    # -------------------------------------------------
    "abhishekam this week",
    "abhishekam next week",
    "abhishekam last week",
    "abhishekam this month",
    "abhishekam next month",
    "abhishekam in february",
    "abhishekam after 4 months",

    # -------------------------------------------------
    # SPONSORSHIP
    # -------------------------------------------------
    "abhishekam sponsorship",
    "abhishekam cost",
    "how much is abhishekam",
    "abhishekam fee at temple",
    "abhishekam fee at home",

    # -------------------------------------------------
    # MOOLA / TYPE
    # -------------------------------------------------
    "moola murthy abhishekam",
    "individual abhishekam",
    "saamoohika abhishekam",

    # -------------------------------------------------
    # VASTRA SAMARPANAM
    # -------------------------------------------------
    "venkateswara abhishekam vastram",
    "andal abhishekam vastram",
    "mahalakshmi vastram",
    "vastra samarpanam andal",

    # -------------------------------------------------
    # COMBINED NATURAL LANGUAGE
    # -------------------------------------------------
    "when is siva abhishekam and how much does it cost",
    "andal abhishekam next month sponsorship",
    "venkateswara abhishekam with vastram",
    "is abhishekam happening this saturday",

    # -------------------------------------------------
    # SPELLING / FUZZY
    # -------------------------------------------------
    "abishekam",
    "abishkam",
    "abishegam",

    # -------------------------------------------------
    # EDGE / UNKNOWN
    # -------------------------------------------------
    "krishna abhishekam",
    "unknown deity abhishekam",

     # ---------------- PAST ----------------
    "siva abhishekam last week",
    "abhishekam yesterday",
    "abhishekam in december 2025",
    "was there any abhishekam last month",

    # ---------------- PRESENT ----------------
    "abhishekam today",
    "is there abhishekam this week",
    "any abhishekam this month",

    # ---------------- FUTURE ----------------
    "siva abhishekam next week",
    "abhishekam next month",
    "abhishekam in march",
    "abhishekam in april 2026",
    "when is abhishekam in may",
    "venkateswara abhishekam in june",
    "siva abhishekam in july",
    "abhishekam in august",
    "abhishekam in september",
    "abhishekam in october",
    "abhishekam in november",
    "abhishekam in december",

    # ---------------- EXPLICIT DATE ----------------
    "siva abhishekam on jan 10",
    "abhishekam on feb 14 2026",
    "is there abhishekam on march 1st",
    "any abhishekam on april 5",

    # Generic
    "kalyanam",
    "kalyanam schedule",
    "when is kalyanam",
    "temple kalyanam",

    # Relative time
    "kalyanam today",
    "kalyanam this week",
    "kalyanam next week",
    "kalyanam this month",
    "kalyanam next month",

    # Month specific
    "kalyanam in february",
    "kalyanam in march",
    "kalyanam in april 2026",
    "venkateswara kalyanam in may",
    "srinivasa kalyanam in june",

    # Explicit date
    "kalyanam on jan 10",
    "kalyanam on feb 14 2026",
    "is there kalyanam on march 1st",

    "kalyanam sponsorship",
    "kalyanam sponsorship details",
    "kalyanam cost",
    "kalyanam price",
    "how much is kalyanam",
    "venkateswara kalyanam sponsorship",
    "srinivasa kalyanam sponsorship",
    "kalyanam temple fee",
    "kalyanam home sponsorship",

    "when is venkateswara kalyanam and how much does it cost",
    "kalyanam next month sponsorship",
    "tell me about kalyanam at the temple",
    "is there any upcoming kalyanam",
    "kalyanam dates and sponsorship",
    "kalyanam happening this saturday",

     # Typos
    "kalyanam",
    "kalynam",
    "kalyanem",

    # Unknown deity
    "krishna kalyanam",
    "unknown deity kalyanam",

    # Ambiguous
    "special kalyanam",
    "any big kalyanam coming up",

    # Stress / vague
    "tell me everything about kalyanam",
]

# =========================================================
# TEST
# =========================================================

@pytest.mark.parametrize("query", ABHISHEKAM_QUERIES)
def test_abhishekam_bot_responses(query):
    response = answer_user(query, message_ts=NOW_TS)

    print("\n" + "=" * 90)
    print(f"QUERY : {query}")
    print("-" * 90)
    print("BOT RESPONSE:\n")
    print(response)
    print("=" * 90)

    # Only ensure bot doesn't crash
    assert response is not None
