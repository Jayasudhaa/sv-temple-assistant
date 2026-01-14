
##backend/satyanarayana_query.py
from datetime import datetime,date
import re
from datetime import datetime
from backend.items_catalog_query import ITEMS_REQUIRED, POOJA_SAMAGRI_URL
from backend.sponsorship_catalog import SPONSORSHIP_CATALOG
from backend.calender_2026 import CALENDAR_2026
import calendar

SATYANARAYANA_SPONSORSHIP_KEYS = {
    "individual": "satyanarayana_swamy_vratham_individual",
    "saamoohika": "satyanarayana_swamy_vratham_saamoohika",
}

def get_satyanarayana_sponsorship():
    ind = SPONSORSHIP_CATALOG.get(
        SATYANARAYANA_SPONSORSHIP_KEYS["individual"]
    )
    grp = SPONSORSHIP_CATALOG.get(
        SATYANARAYANA_SPONSORSHIP_KEYS["saamoohika"]
    )

    if not ind and not grp:
        return None

    lines = ["💰 SPONSORSHIP OPTIONS:\n"]

    if grp:
        lines.append(
            f"• Saamoohika / Group Pooja (at Temple): ${grp['temple_fee']} per family (walk-in)"
        )

    if ind:
        lines.append(
            f"• Individual Pooja (at Temple): ${ind['temple_fee']}"
        )
        if ind.get("home_fee"):
            lines.append(
                f"• Individual Pooja (at Home): ${ind['home_fee']}"
            )

    lines.append("\n📞 Contact Temple Manager to schedule individual pooja.")

    return "\n".join(lines)


def handle_satyanarayana_pooja(q: str, now: datetime) -> str | None:
    q = q.lower()

    if "satyanarayana" not in q:
        return None

    # -------------------------------------------------
    # STORY → handled elsewhere
    # -------------------------------------------------
    if any(w in q for w in [
        "story", "significance", "meaning", "why", "importance", "about"
    ]):
        return None

    # -------------------------------------------------
    # ITEMS REQUIRED
    # -------------------------------------------------
    if any(w in q for w in [
        "item", "items", "required", "bring", "samagri", "material"
    ]):
        info = ITEMS_REQUIRED["satyanarayana"]
        return (
            "🪔 SRI SATYANARAYANA SWAMY POOJA – ITEMS REQUIRED\n\n"
            f"{info['items']}\n\n"
            "📌 NOTE:\n"
            f"• {info['note']}\n"
            f"🔗 {POOJA_SAMAGRI_URL}\n"
        )

    # -------------------------------------------------
    # TIMING + SPONSORSHIP
    # -------------------------------------------------
    sponsorship = get_satyanarayana_sponsorship()
    upcoming = []

    for month, days in CALENDAR_2026.items():
        try:
            month_num = list(calendar.month_name).index(month.capitalize())
        except ValueError:
            continue  # skip if month name is not valid

        for day, info in days.items():
            for key, value in info.items():
                # Normalize all entries to lowercase and check if 'satyanarayana' is mentioned
                if isinstance(value, list) and any("satyanarayana" in v.lower() for v in value):
                    try:
                        d = date(2026, month_num, day)
                        if d >= now.date():
                            upcoming.append(d)
                    except Exception:
                        continue
   
    lines = [
        "🪔 SRI SATYANARAYANA SWAMY POOJA",
        "",
        "📅 TIMING:",
        "• Full Moon Day (Poornima) – 06:30 PM",
        "",
        sponsorship,
        "",
        "",
        "👗 VASTRA SAMARPANAM",
        "",
        "Vastra Samarpana is a devotional offering of clothes symbolizing reverence and devotion.",
        "",
        "💰 TEMPLE PROVIDED (Silk Mark Certified):",
        "• Venkateswara Swamy – First Saturday: $1,116",
        "• Venkateswara Swamy Kalyanam – Second Saturday: $516",
        "• Andal Ammavaru – Third Friday: $301",
        "• Mahalakshmi Ammavaru – Third Saturday: $401",
        "",
        "💰 DEVOTEE PROVIDED:",
        "• Venkateswara Swamy – First Saturday: $516",
        "• Venkateswara Swamy Kalyanam – Second Saturday: $201",
        "• Andal Ammavaru – Third Friday: $151",
        "• Mahalakshmi Ammavaru – Third Saturday: $151",
        "",
        
    ]

    if upcoming:
        upcoming.sort()
        lines.append("")
        lines.append("📅 UPCOMING DATES:")
        for d in upcoming[:3]:
            lines.append(f"• {d.strftime('%B %d, %Y')}")
        lines.append("")


    return "\n".join(lines)
