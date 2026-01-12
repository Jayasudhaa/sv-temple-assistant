#backend/federal_holidays.py
# 
from datetime import date, timedelta

def nth_weekday_of_month(year: int, month: int, weekday: int, n: int) -> date:
    """
    weekday: Monday=0 ... Sunday=6
    n: nth occurrence in month
    """
    d = date(year, month, 1)
    while d.weekday() != weekday:
        d += timedelta(days=1)
    return d + timedelta(weeks=n - 1)


def last_weekday_of_month(year: int, month: int, weekday: int) -> date:
    if month == 12:
        d = date(year, 12, 31)
    else:
        d = date(year, month + 1, 1) - timedelta(days=1)

    while d.weekday() != weekday:
        d -= timedelta(days=1)
    return d

def observe_if_weekend(d: date) -> date:
    if d.weekday() == 5:      # Saturday
        return d - timedelta(days=1)
    if d.weekday() == 6:      # Sunday
        return d + timedelta(days=1)
    return d


def get_federal_holidays(year: int) -> dict[date, str]:
    """
    Returns {date: holiday_name}
    """
    holidays = {}

    # Fixed-date holidays
    holidays[observe_if_weekend(date(year, 1, 1))] = "New Year’s Day"
    holidays[observe_if_weekend(date(year, 7, 4))] = "Independence Day"
    holidays[observe_if_weekend(date(year, 12, 25))] = "Christmas Day"

    # Floating holidays
    holidays[nth_weekday_of_month(year, 1, 0, 3)] = "Martin Luther King Jr. Day"
    holidays[last_weekday_of_month(year, 5, 0)] = "Memorial Day"
    holidays[nth_weekday_of_month(year, 9, 0, 1)] = "Labor Day"
    holidays[nth_weekday_of_month(year, 11, 3, 4)] = "Thanksgiving Day"
    holidays[nth_weekday_of_month(year, 2, 0, 3)] = "Presidents’ Day"

    return holidays

