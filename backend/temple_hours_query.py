

from datetime import datetime,time
from backend.federal_holidays import get_federal_holidays
from backend.calender_2026 import CALENDAR_2026

def handle_temple_hours(q: str, now: datetime) -> str | None:
    q = q.lower().replace("’", "'")

    if not any(w in q for w in ["open", "close", "hours", "timing", "time"]):
        return None

    today = now.date()
    current_time = now.time()
    is_weekend = now.weekday() >= 5

    # ---------------- FEDERAL HOLIDAYS ----------------
    holidays = get_federal_holidays(now.year)
    is_holiday = today in holidays
    holiday_name = holidays.get(today)

    # ---------------- FESTIVALS (DISPLAY ONLY) ----------------
    festival_names = []
    if today.year == 2026:
        month = today.strftime("%B").lower()
        festival_names = CALENDAR_2026.get(month, {}).get(today.day, {}).get("festival", [])

    # ---------------- TIME SLOTS ----------------
    full_day_slot = (time(9, 0), time(20, 0))
    weekday_morning = (time(9, 0), time(12, 0))
    weekday_evening = (time(18, 0), time(20, 0))

    def in_range(a, b):
        return a <= current_time <= b
    
    # ============================================================
    # ✅ NEW: Detect if user is specifically asking "weekday" or "weekend"
    # ============================================================
    wants_weekday = any(w in q for w in ["weekday", "weekdays", "monday", "tuesday", "wednesday", "thursday", "friday"])
    wants_weekend = any(w in q for w in ["weekend", "weekends", "saturday", "sunday", "holiday", "holidays"])

    # ✅ If user asked ONLY weekend → weekend schedule only
    if wants_weekend and not wants_weekday:
        return (
            "⏰ WEEKEND / HOLIDAY TEMPLE HOURS\n\n"
            "• 9:00 AM – 8:00 PM\n"
            "• Cafeteria (Sat–Sun): 12:00 PM – 2:00 PM"
        )

    # ✅ If user asked ONLY weekday → weekday schedule only
    if wants_weekday and not wants_weekend:
        return (
            "⏰ WEEKDAY TEMPLE HOURS (Mon–Fri)\n\n"
            "• 9:00 AM – 12:00 PM\n"
            "• 6:00 PM – 8:00 PM"
        )

    # ✅ If user asked BOTH (rare) → show both
    if wants_weekday and wants_weekend:
        return (
            "⏰ TEMPLE HOURS\n\n"
            "• Weekday (Mon–Fri):\n"
            "  – 9:00 AM – 12:00 PM\n"
            "  – 6:00 PM – 8:00 PM\n\n"
            "• Weekend / Holiday:\n"
            "  – 9:00 AM – 8:00 PM\n\n"
            "• Cafeteria (Sat–Sun): 12:00 PM – 2:00 PM"
        )


    # ---------------- DAY TYPE (HOURS ONLY) ----------------
    if is_holiday:
        day_type = "federal_holiday"
    elif is_weekend:
        day_type = "weekend"
    else:
        day_type = "weekday"

    # ---------------- LABEL ----------------
    if day_type == "federal_holiday" and holiday_name:
        label = holiday_name
    elif day_type == "weekend":
        label = "Weekend"
    else:
        label = "Weekday"

    # ---------------- STATUS LOGIC ----------------
    if day_type in ["federal_holiday", "weekend"]:
        if in_range(*full_day_slot):
            lines = [
                f"🕉️ TEMPLE STATUS: OPEN Until 8 PM ({label})",
                "",
                "• Hours: 9:00 AM – 8:00 PM",
            ]
        else:
            lines = [
                f"🕉️ TEMPLE STATUS: CLOSED NOW ({label})",
                "",
                "• Hours: 9:00 AM – 8:00 PM",
                "• Next opening: 9:00 AM",
            ]

    else:
        # ---------------- WEEKDAY SPLIT HOURS ----------------
        if in_range(*weekday_morning):
            closes_at = "12:00 PM"
        elif in_range(*weekday_evening):
            closes_at = "8:00 PM"
        else:
            closes_at = None

        if closes_at:
            lines = [
                f"🕉️ TEMPLE STATUS: OPEN Until {closes_at} ({label})",
                "",
                "• Weekday Hours:",
                "  – 9:00 AM – 12:00 PM",
                "  – 6:00 PM – 8:00 PM",
            ]
        else:
            next_open = (
                "9:00 AM today" if current_time < time(9, 0)
                else "6:00 PM today" if current_time < time(18, 0)
                else "9:00 AM tomorrow"
            )
            lines = [
                f"🕉️ TEMPLE STATUS: CLOSED NOW ({label})",
                "",
                "• Weekday Hours:",
                "  – 9:00 AM – 12:00 PM",
                "  – 6:00 PM – 8:00 PM",
                f"• Next opening: {next_open}",
            ]

    # ---------------- FESTIVAL INFO (DISPLAY ONLY) ----------------
    if festival_names:
        lines.extend(["", "🎉 Festival Today:"])
        for f in festival_names:
            lines.append(f"• {f}")

    

    lines.extend([
                "",
                "ℹ️ Temple hours shown are for today only."
            ])

    return "\n".join(lines)
