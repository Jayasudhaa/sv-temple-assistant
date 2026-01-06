from backend.ask_temple import answer_user
from datetime import datetime
from zoneinfo import ZoneInfo
import pytest

TZ = ZoneInfo("America/Denver")

def test_vishnu_sahasranam_no_context_leakage():
    ts = int(datetime(2026, 1, 4, 10, 30, tzinfo=TZ).timestamp())
    out = answer_user("siva abhsihekam", message_ts=ts)

    print("\n===== BOT RESPONSE =====\n")
    print(out)

    lowered = out.lower()

    forbidden = [
        "provided temple context",
        "does not contain",
        "not mentioned",
        "documents",
        "context does not",
    ]

    for phrase in forbidden:
        assert phrase not in lowered

    assert "temple manager" in lowered
