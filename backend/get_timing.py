#backend/get_timing.py
# 
from datetime import date


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

# ============================================================
# FORMATTERS
# ============================================================
def resolve_date_range(q: str, now: datetime) -> tuple[list[datetime], str] | None:
    q = q.lower()
    today = now.date()

    # ---------- EXPLICIT DATE ----------
    explicit = parse_explicit_date(q, now)
    if explicit:
        return [explicit], explicit.strftime("%B %d, %Y")

    # ---------- TOMORROW / TODAY / YESTERDAY ----------
    if "tomorrow" in q:
        return [now + timedelta(days=1)], "TOMORROW"

    if "today" in q:
        return [now], "TODAY"

    if "yesterday" in q:
        return [now - timedelta(days=1)], "YESTERDAY"

    # ---------- UPCOMING / WEEK ----------
    if any(w in q for w in ["upcoming", "coming", "upcoming activities", "upcoming events"]):
        start = today
        end = today + timedelta(days=7)
        label = f"UPCOMING ({start:%b %d} – {end:%b %d, %Y})"

    elif "next week" in q or "following week" in q:
        start = today + timedelta(days=(7 - today.weekday()))
        end = start + timedelta(days=6)
        label = f"NEXT WEEK ({start:%b %d} – {end:%b %d, %Y})"

    elif "this week" in q or "week" in q:
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
        label = f"THIS WEEK ({start:%b %d} – {end:%b %d})"

    # ---------- MONTH ----------
    elif "next month" in q:
        year = today.year + (1 if today.month == 12 else 0)
        month = 1 if today.month == 12 else today.month + 1
        start = date(year, month, 1)
        end = date(year, month, calendar.monthrange(year, month)[1])
        label = f"{calendar.month_name[month].upper()} {year}"

    elif "this month" in q:
        start = date(today.year, today.month, 1)
        end = date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
        label = today.strftime("%B").upper()

    elif any(m.lower() in q for m in calendar.month_name if m):
        month = next(m for m in calendar.month_name if m and m.lower() in q)
        month_num = list(calendar.month_name).index(month)
        year = extract_year(q, now)
        start = date(year, month_num, 1)
        end = date(year, month_num, calendar.monthrange(year, month_num)[1])
        label = f"{month.upper()} {year}"

    # ---------- YEAR ----------
    elif "this year" in q or re.search(r"\b20\d{2}\b", q):
        year = extract_year(q, now)
        start = date(year, 1, 1)
        end = date(year, 12, 31)
        label = f"YEAR {year}"

    # ---------- WHAT'S HAPPENING (GENERIC FALLBACK — LAST) ----------
    elif any(p in q for p in [
        "what's happening",
        "whats happening",
        "what is happening",
        "happening now"
    ]):
        return [now], "TODAY"

    else:
        return None

    dates = [
        datetime.combine(start + timedelta(days=i), now.time(), tzinfo=now.tzinfo)
        for i in range((end - start).days + 1)
    ]
    print(f"[DEBUG] DATE RANGE RESOLVED → {label}")
    return dates, label


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

    # ==================================================
    # 🎉 FESTIVALS – FULL YEAR (NO DATE REQUIRED)
    # ==================================================
    if is_festival_query and not any(
    w in q for w in [
        "today", "this", "next", "last", "week", "month", "year"
    ]) and not any(m.lower() in q for m in calendar.month_name if m):

        lines = ["🎉 TEMPLE FESTIVALS – 2026", ""]
        found = False

        for month, days in CALENDAR_2026.items():
            for day, info in days.items():
                if "festival" in info:
                    for name in info["festival"]:
                        found = True
                        lines.append(
                            f"• {name} — {month.capitalize()} {day}, 2026"
                        )

        if not found:
            return None

        return "\n".join(lines)

    # ==================================================
    # 📅 DATE-BASED EVENTS (TODAY / WEEK / MONTH)
    # ==================================================
    resolved = resolve_date_range(q, now)
    if not resolved:
        return None

    dates, label = resolved
    lines = [f"📅 EVENTS – {label}", ""]
    found = False

    for d in dates:
        # Skip past dates ONLY for forward-looking queries
        if d.date() < now.date() and not any(w in q for w in ["last", "previous", "yesterday"]):
            continue

        events = get_calendar_events(d)
        if not events:
            continue

        # Festival-only filtering
        if is_festival_query:
            if "festival" not in events:
                continue
            filtered_events = {"festival": events["festival"]}
        else:
            filtered_events = events

        if not filtered_events:
            continue

        found = True
        lines.append(f"{d:%A, %b %d}")
        lines.extend(format_events(filtered_events))
        lines.append("")

    if not found:
        if label.startswith("UPCOMING") or label.endswith("2026"):
            lines.append("• No festivals or special events listed in this period.")
        else:
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
    "venkateswara": ["venkateswara", "balaji", "tirupati", "srinivasa"],
    "andal": ["andal", "goda", "godha"],
    "hanuman": ["hanuman"],
    "murugan": ["murugan", "subramanya"],
    "ganapati": ["ganapati", "ganesha", "ganapathi"],
    "sai": ["sai", "shirdi"],
    "raghavendra": ["raghavendra", "ragavendra"],
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

    results: list[date] = []

    CAL_YEAR = 2026  # 🔒 calendar truth source
    today = now.date()

    if start_date is None:
        start_date = today
    if end_date is None:
        end_date = date(CAL_YEAR, 12, 31)

    month_index = {
        m.lower(): i + 1 for i, m in enumerate(CALENDAR_2026.keys())
    }

    for month, days in CALENDAR_2026.items():
        month_num = month_index[month.lower()]

        for day, info in days.items():
            for event in info.get("abhishekam", []):

                if deity and deity.lower() not in event.lower():
                    continue

                try:
                    event_day = date(CAL_YEAR, month_num, day)
                except ValueError:
                    continue

                # ✅ HARD FILTER
                if event_day < today:
                    continue
                if not (start_date <= event_day <= end_date):
                    continue

                results.append(event_day)

    results = sorted(set(results))  # ✅ dedupe + sort

    return [
        d.strftime("%B %d, %Y")
        for d in results[:limit]
    ]


def get_abhishekam_sponsorships(deity: str | None):
    results = []

    for s in SPONSORSHIP_CATALOG.values():
        if s.get("category") != "abhishekam":
            continue

        name = s.get("name", "").lower()

        # ----------------------------------------
        # NO DEITY SPECIFIED → SHOW ALL
        # ----------------------------------------
        if not deity:
            results.append(s)
            continue

        # ----------------------------------------
        # DEITY-SPECIFIC FILTERING
        # ----------------------------------------
        if deity == "venkateswara" and any(x in name for x in ["venkateswara", "srinivasa"]):
            results.append(s)
        elif deity == "andal" and "andal" in name:
            results.append(s)
        elif deity == "mahalakshmi" and "mahalakshmi" in name:
            results.append(s)
        elif deity in {"siva", "ganapati", "murugan", "hanuman", "sai", "raghavendra"}:
            if any(x in name for x in [
                "shiva", "ganapathi", "murugan",
                "hanuman", "sai", "ragavendra"
            ]):
                results.append(s)

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
    q = q.lower()
    if "abhishekam" not in q:
        return None

    deity = extract_deity(q)

    DEITY_NORMALIZATION = {
        "goda": "andal",
        "godha": "andal",
        "andal": "andal",
        "lakshmi": "mahalakshmi",
        "mahalakshmi": "mahalakshmi",
        "srinivasa": "venkateswara",
        "venkateswara": "venkateswara",
        "ganapathi": "ganapati",
        "ganapati": "ganapati",
        "ragavendra": "raghavendra",
        "raghavendra": "raghavendra",
    }

    deity = DEITY_NORMALIZATION.get(deity, deity)

    DISPLAY_DEITY_NAMES = {
        "venkateswara": "Sri Venkateswara",
        "andal": "Sri Andal",
        "mahalakshmi": "Sri Mahalakshmi",
        "siva": "Sri Siva",
        "hanuman": "Sri Hanuman",
        "murugan": "Sri Murugan",
        "ganapati": "Sri Ganapathi",
        "raghavendra": "Sri Raghavendra",
        "sai": "Sri Sai Baba",
    }

    title = (
        f"🪔 {DISPLAY_DEITY_NAMES[deity]} Abhishekam"
        if deity in DISPLAY_DEITY_NAMES
        else "🪔 Abhishekam Schedule"
    )

    lines = [title, ""]

    # ---------------- WEEKLY RECURRENCE ----------------
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
            "📌 Weekly Schedule",
            f"• Happens every {extract_weekly_pattern(WEEKLY_EVENTS[wk_key])}",
            ""
        ])
    # ==================================================
    # 🔁 RELATIVE DATE FILTER (ADD THIS BLOCK)
    # ==================================================
    today = now.date()
    start_date = end_date = None
    date_filter_applied = False

    if "next week" in q:
        start_date = today + timedelta(days=(7 - today.weekday()))
        end_date = start_date + timedelta(days=6)

    elif "this week" in q or "week" in q:
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)

    elif "next month" in q:
        year = today.year + (1 if today.month == 12 else 0)
        month = 1 if today.month == 12 else today.month + 1
        start_date = date(year, month, 1)
        end_date = date(year, month, calendar.monthrange(year, month)[1])

    elif "this month" in q:
        start_date = date(today.year, today.month, 1)
        end_date = date(today.year, today.month,
                        calendar.monthrange(today.year, today.month)[1])
        
    # ---------------- EXPLICIT MONTH NAME (ONLY IF NO RELATIVE FILTER) ----------------
    if not date_filter_applied:
        year = now.year
        for i, m in enumerate(calendar.month_name):
            if m and m.lower() in q:
                start_date = date(year, i, 1)
                end_date = date(year, i, calendar.monthrange(year, i)[1])
                break


    # ---------------- UPCOMING DATES ----------------
    dates = get_calendar_abhishekam_dates(
        deity=deity,
        now=now,
        start_date=start_date,
        end_date=end_date
    )

    lines.append("📅 Upcoming Dates")
    if dates:
        lines.extend(f"• {d}" for d in dates)
    else:
        lines.append("• No Abhishekam dates listed.")

    # ---------------- SPONSORSHIP ----------------
    sponsorships = get_abhishekam_sponsorships(deity)
    if sponsorships:
        lines.extend(["", "💰 Sponsorship"])
        for s in sponsorships:
            lines.append(f"• {s['name']}")
            if s.get("temple_fee") is not None:
                lines.append(f"  – Temple: ${s['temple_fee']}")
            if s.get("home_fee") is not None:
                lines.append(f"  – Home: ${s['home_fee']}")
            if s.get("annual_fee") is not None:
                lines.append(f"  – Annual: ${s['annual_fee']}")

    # ---------------- VASTRA SAMARPANAM ----------------
    if deity in {"venkateswara", "andal", "mahalakshmi"}:
        vastras = get_vastra_samarpanam_for_deity(deity)
        if vastras:
            lines.extend(["", "🧵 Vastra Samarpanam"])
            for v in vastras:
                lines.append(f"• {v['name']}")
                if v.get("temple_fee") is not None:
                    lines.append(f"  – Sponsorship: ${v['temple_fee']}")

    return "\n".join(lines)