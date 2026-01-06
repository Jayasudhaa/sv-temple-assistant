import pytest
from datetime import datetime
from zoneinfo import ZoneInfo
from backend.ask_temple import answer_user

TZ = ZoneInfo("America/Denver")

FORBIDDEN_PHRASES = [
    "provided temple context",
    "does not contain",
    "not mentioned",
    "documents focus on",
    "context does not",
    "not specifically detailed",
]

MANAGER_MARKERS = [
    "temple manager",
    "phone:",
    "email:",
]

DONATE_URL = "https://svtempleco.org/Home/Donate.html"


TEST_CASES = [
    # -----------------------------
    # HOURS
    # -----------------------------
    ("Weekday hours", {}),
    ("Weekend hours", {}),
    ("Holiday hours", {}),

    # -----------------------------
    # DONATION
    # -----------------------------
    ("Donate", {"must_contain": [DONATE_URL]}),

    # -----------------------------
    # FESTIVALS / CALENDAR
    # -----------------------------
    ("Festivals", {}),
    ("Festival", {}),
    ("Calendar", {}),
    ("Temple Calendar", {}),

    # -----------------------------
    # NAKSHATRA / CALENDAR DATA
    # -----------------------------
    ("Purvashada", {"must_not_leak": True}),
    ("Rohini", {"must_not_leak": True}),

    # -----------------------------
    # FOOD
    # -----------------------------
    ("Laddu", {}),
    ("Vada", {}),

    # -----------------------------
    # FAMILY / GENERIC
    # -----------------------------
    ("Amma", {}),
    ("Appa", {}),
    ("Mother", {}),
    ("Father", {}),
    ("Ammavaru", {}),

    # -----------------------------
    # STOTRAS / RAG-SENSITIVE
    # -----------------------------
    ("Lalitha Sahasranamam", {"require_manager": True}),
    ("Vishnu Sahasranamam", {"require_manager": True}),
    ("Sukthams", {"require_manager": True}),
    ("Naama Sankeerthanams", {"require_manager": True}),
    ("Sahasranamams", {}),

    # -----------------------------
    # RUDRAM
    # -----------------------------
    ("Rudram", {}),

    # -----------------------------
    # HOLIDAYS
    # -----------------------------
    ("Christmas", {}),
    ("Thanksgiving", {"require_manager": True}),
    ("Memorial Day", {}),
    ("Labor Day", {"require_manager": True}),
    ("Martin Luther King Day", {"require_manager": True}),
    ("Presidents Day", {"require_manager": True}),

    # -----------------------------
    # EVENTS / APPRECIATION
    # -----------------------------
    ("Volunteer Appreciation Day", {}),

    # -----------------------------
    # PUJAS
    # -----------------------------
    ("Kumari Puja", {}),
    ("Kanya Puja", {}),

    # -----------------------------
    # SYMBOLS / OBJECTS
    # -----------------------------
    ("Lotus", {}),
    ("Swastika", {}),
    ("Snake", {}),
    ("Darbha", {}),
    ("Dollar", {}),

    # -----------------------------
    # PHILOSOPHY
    # -----------------------------
    ("Sponsorship", {}),
    ("Hinduisam", {}),
    ("Sanathana Dharma", {}),

    # -----------------------------
    # CONTACT / IDENTITY
    # -----------------------------
    ("Website", {}),
    ("Address", {}),
    ("Phone", {}),
    ("email", {}),
    ("Sri Venkateswara Temple of Colorado", {}),

    # -----------------------------
    # DAILY WORSHIP
    # -----------------------------
    ("Nitya Archana", {}),
    ("Mailing List", {}),
    ("Learning", {}),
    ("Dwitiya", {}),
]


@pytest.mark.parametrize("query,expectations", TEST_CASES)
def test_rag_queries(query, expectations):
    ts = int(datetime(2026, 1, 4, 9, 45, tzinfo=TZ).timestamp())
    out = answer_user(query, message_ts=ts)
    lowered = out.lower()

    # -----------------------------
    # 1️⃣ NO RAG CONTEXT LEAKAGE
    # -----------------------------
    for phrase in FORBIDDEN_PHRASES:
        assert phrase not in lowered, (
            f"\n❌ Forbidden phrase '{phrase}' found for query: {query}\n\n"
            f"===== BOT OUTPUT =====\n{out}\n"
        )

    # -----------------------------
    # 2️⃣ MUST CONTAIN URL
    # -----------------------------
    if "must_contain" in expectations:
        for item in expectations["must_contain"]:
            assert item.lower() in lowered, (
                f"\n❌ Expected '{item}' not found for query: {query}\n\n"
                f"{out}"
            )

    # -----------------------------
    # 3️⃣ REQUIRE MANAGER CONTACT
    # -----------------------------
    if expectations.get("require_manager"):
        assert any(m in lowered for m in MANAGER_MARKERS), (
            f"\n❌ Temple Manager contact missing for query: {query}\n\n"
            f"{out}"
        )
