from datetime import datetime, date
from typing import Optional

from backend.constants import WEEKLY_EVENTS
from backend.calender_2026 import CALENDAR_2026
from backend.get_timing import extract_weekly_pattern
from backend.sponsorship_catalog import SPONSORSHIP_CATALOG


HUMAN_WEDDING_KEYWORDS = [
    "marriage", "wedding", "bride", "groom",
    "human", "can we do wedding", "hindu wedding"
]

def handle_kalyanam(q: str, now: datetime) -> Optional[str]:
    q = q.lower()

    if "kalyanam" not in q:
        return None

    # --------------------------------------------------
    # HUMAN WEDDING CHECK (STRICT SEPARATION)
    # --------------------------------------------------
    if any(k in q for k in HUMAN_WEDDING_KEYWORDS):
        return (
            "🪔 Hindu Wedding Ceremony\n\n"
            "• A Hindu wedding (Vivaha) is a sacred samskara performed for individuals\n"
            "• It is traditionally conducted by family priests at homes or wedding venues\n"
            "• The temple does not perform human wedding ceremonies\n"
            "• For spiritual guidance or priest services, please contact the Temple Manager"
        )

    # --------------------------------------------------
    # DETERMINE WHICH KALYANAM USER MEANS
    # --------------------------------------------------
    deity_key = "venkateswara"
    title = "🪔 Sri Venkateswara Swamy Kalyanam"

    if any(w in q for w in ["goda", "andal"]):
        deity_key = "goda"
        title = "🪔 Sri Goda (Andal) Kalyanam"
    elif "meenakshi" in q:
        deity_key = "meenakshi"
        title = "🪔 Sri Meenakshi Kalyanam"
    elif "tulasi" in q:
        deity_key = "tulasi"
        title = "🪔 Sri Tulasi Kalyanam"

    lines = [title, ""]

    # --------------------------------------------------
    # DESCRIPTION (ONLY FOR VENKATESWARA)
    # --------------------------------------------------
    if deity_key == "venkateswara" and any(
        w in q for w in ["everything", "about", "details", "explain", "tell me"]
    ):
        lines.extend([
            "• Kalyanam is the divine celestial wedding of Lord Venkateswara with Sri Devi and Bhu Devi",
            "• It is performed as an arjitha seva for the well-being of devotees and families",
            "• The ceremony includes sankalpam, mangalya dharanam, and Vedic chants",
            ""
        ])

    # --------------------------------------------------
    # WEEKLY RECURRENCE (ONLY FOR VENKATESWARA)
    # --------------------------------------------------
    if deity_key == "venkateswara":
        wk_key = "venkateswara swamy kalyanam"
        if wk_key in WEEKLY_EVENTS:
            lines.extend([
                "📌 Schedule",
                f"• Happens every {extract_weekly_pattern(WEEKLY_EVENTS[wk_key])}",
                ""
            ])

    # --------------------------------------------------
    # CALENDAR 2026 DATES (DEITY-SPECIFIC)
    # --------------------------------------------------
    upcoming = []

    month_index = {
        m.lower(): i + 1 for i, m in enumerate(CALENDAR_2026.keys())
    }

    for month, days in CALENDAR_2026.items():
        month_num = month_index[month.lower()]

        for day, info in days.items():
            for event in info.get("kalyanam", []):
                e = event.lower()

                if deity_key == "venkateswara" and "venkateswara" not in e:
                    continue
                if deity_key == "goda" and not any(x in e for x in ["goda", "andal"]):
                    continue
                if deity_key == "meenakshi" and "meenakshi" not in e:
                    continue
                if deity_key == "tulasi" and "tulasi" not in e:
                    continue

                try:
                    d = date(2026, month_num, day)
                except ValueError:
                    continue

                if d >= now.date():
                    upcoming.append(d)

    upcoming.sort()

    lines.append("📅 Upcoming Dates")
    if upcoming:
        for d in upcoming[:3]:
            lines.append(f"• {d.strftime('%B %d, %Y')}")
    else:
        lines.append("• No upcoming Kalyanam dates listed.")

    # --------------------------------------------------
    # SPONSORSHIP (FILTERED BY DEITY NAME)
    # --------------------------------------------------
    sponsorships = [
        s for s in SPONSORSHIP_CATALOG.values()
        if "kalyanam" in s.get("name", "").lower()
        and deity_key in s.get("name", "").lower()
    ]

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

    return "\n".join(lines)
