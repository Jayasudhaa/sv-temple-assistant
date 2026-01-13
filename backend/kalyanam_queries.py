from datetime import datetime, date
from typing import Optional

from backend.constants import WEEKLY_EVENTS
from backend.calender_2026 import CALENDAR_2026
from backend.get_timing import extract_weekly_pattern
from backend.sponsorship_catalog import SPONSORSHIP_CATALOG

def norm(text: str) -> str:
    return (
        text.lower()
        .replace("–", "-")
        .replace("—", "-")
        .strip()
    )


DEITY_ALIASES = {
    "venkateswara": ["venkateswara", "kalyanotsavam"],
    "goda": ["goda", "andal"],
    "meenakshi": ["meenakshi"],
    "tulasi": ["tulasi"],
}


HUMAN_WEDDING_KEYWORDS = [
    "marriage", "wedding", "bride", "groom",
    "human", "can we do wedding", "hindu wedding"
]

def add_fee(label, value):
    if value is not None:
        return f"  – {label}: ${value}"
    return None

def handle_kalyanam(q: str, now: datetime) -> Optional[str]:
    q = q.lower()

    if "kalyanam" not in q:
        return None

    # --------------------------------------------------
    # HUMAN WEDDING CHECK (STRICT)
    # --------------------------------------------------
    if any(k in q for k in HUMAN_WEDDING_KEYWORDS):
        return (
            "🪔 Hindu Wedding Ceremony\n\n"
            "• A Hindu wedding (Vivaha) is a sacred samskara performed for individuals\n"
            "• It is traditionally conducted by family priests at homes or wedding venues\n"
            "• The temple does not perform human wedding ceremonies\n"
            "• For priest services, please contact the Temple Manager"
        )

    # --------------------------------------------------
    # DETERMINE DEITY
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
    # DESCRIPTION (VENKATESWARA ONLY)
    # --------------------------------------------------
    if deity_key == "venkateswara" and any(
        w in q for w in ["about", "details", "explain", "tell me"]
    ):
        lines.extend([
            "• Kalyanam is the divine celestial wedding of Lord Venkateswara",
            "• It is performed as an arjitha seva for family well-being",
            "• The ceremony includes sankalpam and Vedic chants",
            ""
        ])

    # --------------------------------------------------
    # WEEKLY SCHEDULE (VENKATESWARA ONLY)
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
    # CALENDAR 2026 UPCOMING DATES
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
    # SPONSORSHIP (CORRECT + ROBUST)
    # --------------------------------------------------
    aliases = DEITY_ALIASES.get(deity_key, [])

    sponsorships = [
        s for s in SPONSORSHIP_CATALOG.values()
        if s.get("category") == "kalyanam"
        and any(a in norm(s.get("name", "")) for a in aliases)
    ]

    if sponsorships:
        lines.extend(["", "💰 Sponsorship"])
        for s in sponsorships:
            lines.append(f"• {s['name']}")

            for fee_line in [
                add_fee("Temple", s.get("temple_fee")),
                add_fee("Home", s.get("home_fee")),
                add_fee("Annual", s.get("annual_fee")),
            ]:
                if fee_line:
                    lines.append(fee_line)

    return "\n".join(lines)