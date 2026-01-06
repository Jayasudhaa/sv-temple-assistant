from datetime import datetime
from zoneinfo import ZoneInfo

from backend.ask_temple import is_supported_federal_holiday

TZ = ZoneInfo("America/Denver")

def test_new_year():
    ok, name = is_supported_federal_holiday(datetime(2026, 1, 1, tzinfo=TZ))
    assert ok and name == "New Year’s Day"

def test_memorial_day():
    ok, name = is_supported_federal_holiday(datetime(2026, 5, 25, tzinfo=TZ))
    assert ok and name == "Memorial Day"

def test_independence_day():
    ok, name = is_supported_federal_holiday(datetime(2026, 7, 4, tzinfo=TZ))
    assert ok and name == "Independence Day"

def test_labor_day():
    ok, name = is_supported_federal_holiday(datetime(2026, 9, 7, tzinfo=TZ))
    assert ok and name == "Labor Day"

def test_thanksgiving():
    ok, name = is_supported_federal_holiday(datetime(2026, 11, 26, tzinfo=TZ))
    assert ok and name == "Thanksgiving Day"

def test_christmas():
    ok, name = is_supported_federal_holiday(datetime(2026, 12, 25, tzinfo=TZ))
    assert ok and name == "Christmas Day"

def test_non_holiday():
    ok, name = is_supported_federal_holiday(datetime(2026, 3, 18, tzinfo=TZ))
    assert ok is False
