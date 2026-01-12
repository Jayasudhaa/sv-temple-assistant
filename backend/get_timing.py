#backend/get_timing.py
# 
from datetime import date,time
from zoneinfo import ZoneInfo

import calendar
from datetime import datetime, timedelta,date
from typing import Optional, List
import os
import re
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
from backend.calender_2026 import CALENDAR_2026
from backend.federal_holidays import get_federal_holidays,nth_weekday_of_month
from backend.sponsorship_catalog import SPONSORSHIP_CATALOG
from backend.constants import WEEKLY_EVENTS

# ============================================================
# DATA ACCESS (CALENDAR + HOLIDAYS)
# ============================================================

def get_calendar_events(date: datetime) -> dict:
    """
    Returns merged temple + federal holiday events for a date.
    """
    events = {}

    # ---------------- TEMPLE EVENTS ----------------
    if date.year == 2026:
        month = date.strftime("%B").lower()
        events = CALENDAR_2026.get(month, {}).get(date.day, {}).copy()

    # ---------------- FEDERAL HOLIDAYS ----------------
    holidays = get_federal_holidays(date.year)
    holiday = holidays.get(date.date())
    if holiday:
        events.setdefault("holiday", []).append(holiday)

    return events

def load_lunar_dates(year: int, lunar_type: str) -> list[str]:
    """
    lunar_type: 'Fullmoon' or 'Amavasya'
    """
    base = os.path.join(
        "data_raw",
        "Events",
        str(year),
        lunar_type
    )

    if not os.path.isdir(base):
        logger.error("Lunar directory not found: %s", base)
        return []

    results = []

    for fname in os.listdir(base):
        if not fname.endswith(".txt"):
            continue

        path = os.path.join(base, fname)
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    clean = line.strip()
                    if clean:
                        results.append(clean)
        except Exception as e:
            logger.error("Error reading lunar file %s", path, exc_info=True)

    return results

def handle_lunar_dates(q: str, now: datetime) -> str | None:
    year_match = re.search(r"\b(20\d{2})\b", q)
    year = int(year_match.group(1)) if year_match else now.year

    is_poornima = any(w in q for w in ["poornima", "purnima", "full moon"])
    is_amavasya = any(w in q for w in ["amavasya", "new moon", "no moon"])

    if not (is_poornima or is_amavasya):
        return None

    months = [
        "january","february","march","april","may","june",
        "july","august","september","october","november","december"
    ]

    target_month = next((m for m in months if m in q), None)

    # -------------------------------
    # LOAD DATA
    # -------------------------------
    if is_poornima:
        raw_dates = load_lunar_dates(year, "Fullmoon")
        title = "🌕 POORNIMA DATES"
    else:
        raw_dates = load_lunar_dates(year, "Amavasya")
        title = "🌑 AMAVASYA DATES"

    if not raw_dates:
        return (
            f"{title} ({year})\n"
            "• Dates not listed.\n\n"
           
        )

    # -------------------------------
    # MONTH FILTER
    # -------------------------------
    if target_month:
        raw_dates = [
            d for d in raw_dates
            if target_month.capitalize() in d
        ]

    if not raw_dates:
        return (
            f"{title} ({target_month.capitalize()} {year})\n"
            "• No dates listed.\n\n"
            
        )

    suffix = (
        f" ({target_month.capitalize()} {year})"
        if target_month else f" ({year})"
    )

    lines = [title + suffix]
    for d in raw_dates:
        lines.append(f"• {d}")

    
    return "\n".join(lines)

# ============================================================
# DATE PARSING & RANGE HELPERS
# ============================================================

def parse_explicit_date(q: str, now: datetime) -> datetime | None:
    """
    Parses queries like:
    - jan 22
    - jan 22nd
    - jan 22 2026
    - jan 22nd 2026
    """
    months = {
        "jan": 1, "january": 1,
        "feb": 2, "february": 2,
        "mar": 3, "march": 3,
        "apr": 4, "april": 4,
        "may": 5,
        "jun": 6, "june": 6,
        "jul": 7, "july": 7,
        "aug": 8, "august": 8,
        "sep": 9, "september": 9,
        "oct": 10, "october": 10,
        "nov": 11, "november": 11,
        "dec": 12, "december": 12,
    }

    for name, month_num in months.items():
        if name in q:
            day_match = re.search(r"\b(\d{1,2})(st|nd|rd|th)?\b", q)
            if not day_match:
                continue

            day = int(day_match.group(1))

            year_match = re.search(r"\b(20\d{2})\b", q)
            year = int(year_match.group(1)) if year_match else now.year

            try:
                return datetime(year, month_num, day, tzinfo=now.tzinfo)
            except ValueError:
                return None

    return None

def next_week_range(now: datetime) -> tuple[date, date]:
    today = now.date()

    # End of THIS week (Sunday)
    days_to_sunday = 6 - today.weekday()
    this_week_end = today + timedelta(days=days_to_sunday)

    # Next week = Monday → Sunday
    start = this_week_end + timedelta(days=1)
    end = start + timedelta(days=6)

    return start, end

# ============================================================
# FORMATTERS
# ============================================================

def format_events(events: dict) -> list[str]:
    lines = []
    for _, items in events.items():
        for item in items:
            lines.append(f"• {item}")
    return lines

def extract_year(q: str, now: datetime) -> int:
    match = re.search(r"\b(20\d{2})\b", q)
    return int(match.group(1)) if match else now.year


def extract_weekly_pattern(schedule: str) -> str:
    # "3rd Friday 11:00 AM – Sri Andal Abhishekam"
    return schedule.split("–")[0].strip()

# ============================================================
# GENERIC CALENDAR HANDLERS
# ============================================================
def handle_calendar_events(q: str, now: datetime) -> str | None:
    q = q.lower()
    is_festival_query = "festival" in q or "festivals" in q

    # ---------------- FESTIVAL NAME SEARCH ----------------
    festival_name_match = None
    for month, days in CALENDAR_2026.items():
        for day, info in days.items():
            for fest in info.get("festival", []):
                if fest.lower() in q:
                    festival_name_match = fest
                    dates = [
                        datetime(2026, list(calendar.month_name).index(month.capitalize()), day, tzinfo=now.tzinfo)
                    ]
                    label = fest.upper()
                    break


    explicit = parse_explicit_date(q, now)
    if explicit:
        dates = [explicit]
        label = explicit.strftime("%B %d, %Y")

    else:
        # ---------------- RELATIVE DAY ----------------
        if "today" in q:
            dates = [now]
            label = "TODAY"

        elif "tomorrow" in q:
            dates = [now + timedelta(days=1)]
            label = "TOMORROW"

        elif "yesterday" in q:
            dates = [now - timedelta(days=1)]
            label = "YESTERDAY"

        # ---------------- WEEK ----------------
        elif "next week" in q:
            start, end = next_week_range(now)
            dates = [
                datetime.combine(start + timedelta(days=i), now.time(), tzinfo=now.tzinfo)
                for i in range((end - start).days + 1)
            ]
            label = f"NEXT WEEK ({start:%b %d} – {end:%b %d, %Y})"

        elif "last week" in q:
            today = now.date()
            start = today - timedelta(days=today.weekday() + 7)
            end = start + timedelta(days=6)
            dates = [
                datetime.combine(start + timedelta(days=i), now.time(), tzinfo=now.tzinfo)
                for i in range(7)
            ]
            label = f"LAST WEEK ({start:%b %d} – {end:%b %d, %Y})"

        elif "this week" in q or "week" in q:
            start = now
            end = now + timedelta(days=(6 - now.weekday()))
            dates = []
            d = start
            while d <= end:
                dates.append(d)
                d += timedelta(days=1)
            label = f"THIS WEEK ({start:%b %d} – {end:%b %d})"


        # ---------------- MONTH ----------------
        elif "this month" in q:
            dates = [
                datetime(now.year, now.month, d, tzinfo=now.tzinfo)
                for d in range(1, calendar.monthrange(now.year, now.month)[1] + 1)
            ]
            label = now.strftime("%B").upper()

        elif any(m.lower() in q for m in calendar.month_name if m):
            month = next(m for m in calendar.month_name if m and m.lower() in q)
            month_num = list(calendar.month_name).index(month)

            year_match = re.search(r"\b(20\d{2})\b", q)
            year = int(year_match.group(1)) if year_match else now.year

            dates = [
                datetime(year, month_num, d, tzinfo=now.tzinfo)
                for d in range(1, calendar.monthrange(year, month_num)[1] + 1)
            ]
            label = f"{month.upper()} {year}"

        # ---------------- YEAR ----------------
        elif "this year" in q or re.search(r"\b20\d{2}\b", q):
            year_match = re.search(r"\b(20\d{2})\b", q)
            year = int(year_match.group(1)) if year_match else now.year

            dates = [
                datetime(year, m, d, tzinfo=now.tzinfo)
                for m in range(1, 13)
                for d in range(1, calendar.monthrange(year, m)[1] + 1)
            ]
            label = f"YEAR {year}"
        # ---------------- FESTIVAL DEFAULT (NO DATE GIVEN) ----------------
        elif is_festival_query:
            dates = [
                datetime(now.year, now.month, d, tzinfo=now.tzinfo)
                for d in range(1, calendar.monthrange(now.year, now.month)[1] + 1)
            ]
            label = f"{now.strftime('%B').upper()} (FESTIVALS)"    

        else:
            return None

    # ---------------- COLLECT EVENTS ----------------
    lines = [f"📅 EVENTS – {label}", ""]
    found = False

    for d in dates:
        # ✅ CRITICAL FIX: skip past dates
        # ✅ skip past dates ONLY for relative-day queries
        if any(w in q for w in ["today", "tomorrow", "next week"]) and d.date() < now.date():
            continue


        events = get_calendar_events(d)

        if not events:
            continue

        # Festival-only filtering
        filtered_events = {}

        if is_festival_query:
            if "festival" in events:
                filtered_events["festival"] = events["festival"]
        else:
            filtered_events = events

        if not filtered_events:
            continue

        found = True
        lines.append(f"{d:%A, %b %d}")
        lines.extend(format_events(filtered_events))
        lines.append("")


    if not found:
        lines.append("• No special events scheduled.")

    return "\n".join(lines)


def handle_nth_weekday(q: str, now: datetime) -> str | None:
    q = q.lower()

    mapping = {
        "1st": 1, "2nd": 2, "3rd": 3, "4th": 4
    }
    weekday_map = {
        "sat": 5,
        "sun": 6
    }

    for k, n in mapping.items():
        for w, wd in weekday_map.items():
            if k in q and w in q:
                d = nth_weekday_of_month(now.year, now.month, wd, n)
                event_date = datetime.combine(d, now.time(), tzinfo=now.tzinfo)

                events = get_calendar_events(event_date)
                lines = [f"📅 {k.capitalize()} {w.capitalize()} – {event_date:%b %d}", ""]

                if events:
                    lines.extend(format_events(events))
                else:
                    lines.append("• No special events.")

                return "\n".join(lines)


    return None

# ============================================================
# DOMAIN: ABHISHEKAM
# ============================================================

def extract_deity(q: str) -> str | None:
    DEITY_MAP = {
        "siva": ["siva", "shiva"],
        "venkateswara": ["venkateswara", "balaji", "tirupati"],
        "hanuman": ["hanuman"],
        "murugan": ["murugan", "subramanya"],
        "ganapati": ["ganapati", "ganesha"],
        "sai": ["sai", "shirdi"],
        "raghavendra": ["raghavendra"],
    }

    for deity, keys in DEITY_MAP.items():
        if any(k in q for k in keys):
            return deity
    return None

def get_calendar_abhishekam_dates(
    deity: Optional[str],
    now: datetime,
    limit: int = 2,
    start_date: date | None = None,
    end_date: date | None = None
) -> list[str]:

    results = []
    today = now.date()
    year = now.year

    # DEFAULT RANGE = today → end of year
    if start_date is None:
        start_date = today
    if end_date is None:
        end_date = date(year, 12, 31)

    month_index = {
        m.lower(): i + 1 for i, m in enumerate(CALENDAR_2026.keys())
    }

    for month, days in CALENDAR_2026.items():
        month_num = month_index[month.lower()]

        for day, info in days.items():
            abhishekams = info.get("abhishekam", [])

            for event in abhishekams:
                if deity and deity.lower() not in event.lower():
                    continue

                try:
                    event_day = date(year, month_num, day)
                except ValueError:
                    continue

                # ✅ RANGE FILTER (FIXES OLD DATES + WEEK ISSUES)
                if not (start_date <= event_day <= end_date):
                    continue

                results.append(event_day)

    results.sort()

    return [
        d.strftime("%B %d, %Y")
        for d in results[:limit]
    ]

def get_abhishekam_sponsorships(deity: Optional[str]) -> List[dict]:
    results = []

    for item in SPONSORSHIP_CATALOG.values():
        if item.get("category") != "abhishekam":
            continue

        if deity and deity in item.get("name", "").lower():
            results.append(item)

    if not results:
        for item in SPONSORSHIP_CATALOG.values():
            if item.get("category") == "abhishekam" and "individual" in item["name"].lower():
                results.append(item)
            if item.get("category") == "abhishekam" and "saamoohika" in item["name"].lower():
                results.append(item)

    return results


def get_vastra_samarpanam_for_deity(deity: str) -> List[dict]:
    results = []

    for item in SPONSORSHIP_CATALOG.values():
        if item.get("category") != "vastra_samarpanam":
            continue
        if deity in item.get("name", "").lower():
            results.append(item)

    return results

def handle_abhishekam(q: str, now: datetime) -> Optional[str]:
    if "abhishekam" not in q.lower():
        return None

    deity = extract_deity(q)
    year = now.year

    title = (
        f"🪔 {deity.title()} Abhishekam"
        if deity else
        "🪔 Abhishekam Schedule"
    )

    lines = [title, ""]

    # --------------------------------------------------
    # WEEKLY RECURRENCE
    # --------------------------------------------------
    WEEKLY_KEY_MAP = {
        "venkateswara": "venkateswara swamy abhishekam",
        "andal": "andal abhishekam",
        "mahalakshmi": "mahalakshmi abhishekam",
        "siva": "siva abhishekam",
        "hanuman": "hanuman abhishekam",
        "murugan": "murugan abhishekam",
        "ganapati": "ganapati abhishekam",
        "raghavendra": "raghavendra swamy abhishekam",
        "sai": "sai baba abhishekam",
    }

    wk_key = WEEKLY_KEY_MAP.get(deity)
    if wk_key and wk_key in WEEKLY_EVENTS:
        lines.extend([
            "📌 Schedule",
            f"• Happens every {extract_weekly_pattern(WEEKLY_EVENTS[wk_key])}",
            ""
        ])
    # --- MONTH FILTER (if mentioned in query) ---
    month = None
    for i, m in enumerate(calendar.month_name):
        if m and m.lower() in q:
            month = i
            break

    start_date = None
    end_date = None

    if month:
        year = now.year
        start_date = date(year, month, 1)
        end_date = date(year, month, calendar.monthrange(year, month)[1])

    # --------------------------------------------------
    # CALENDAR DATES (NEXT 2)
    # --------------------------------------------------
    dates = get_calendar_abhishekam_dates(
    deity,
    now,
    start_date=start_date,
    end_date=end_date
)



    lines.append("📅 Upcoming Dates")
    if dates:
        for d in dates:
            lines.append(f"• {d}")
    else:
        lines.append("• No Abhishekam dates listed in the calendar.")

    # --------------------------------------------------
    # SPONSORSHIP
    # --------------------------------------------------
    sponsorships = get_abhishekam_sponsorships(deity)

    if sponsorships:
        lines.extend(["", "💰 Sponsorship"])
        for s in sponsorships:
            lines.append(f"• {s['name']}")
            if s.get("temple_fee"):
                lines.append(f"  – Temple: ${s['temple_fee']}")
            if s.get("home_fee"):
                lines.append(f"  – Home: ${s['home_fee']}")
            if s.get("annual_fee"):
                lines.append(f"  – Annual: ${s['annual_fee']}")

    # --------------------------------------------------
    # VASTRA SAMARPANAM (MAIN DEITIES ONLY)
    # --------------------------------------------------
    if deity in {"venkateswara", "andal", "mahalakshmi"}:
        vastras = get_vastra_samarpanam_for_deity(deity)

        if vastras:
            lines.extend(["", "🧵 Vastra Samarpanam"])
            for v in vastras:
                lines.append(f"• {v['name']}")
                if v.get("temple_fee"):
                    lines.append(f"  – Sponsorship: ${v['temple_fee']}")

    return "\n".join(lines)

