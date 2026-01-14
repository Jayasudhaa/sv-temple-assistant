from datetime import datetime
from backend.temple_info_query import TEMPLE_INFO
from backend.federal_holidays import observe_if_weekend
from backend.sponsorship_catalog import SPONSORSHIP_CATALOG

FOOD_KEYWORDS = {
    "annadanam",
    "anna danam",
    "food",
    "cafeteria",
    "lunch",
    "meal",
    "prasadam",
}


def handle_food(q: str, now: datetime) -> str | None:
    q = q.lower()

    # -------------------------------------------------
    # 1️⃣ ANNADANAM / FOOD SPONSORSHIP (HIGHEST PRIORITY)
    # -------------------------------------------------
    if any(w in q for w in [
        "annadanam sponsor",
        "annadanam sponsorship",
        "sponsor annadanam",
        "annadanam amount",
        "annadanam donation",
        "food sponsorship",
        "anna danam sponsor",
    ]):
        lines = ["🍽️ ANNADANAM SPONSORSHIP", ""]

        for item in SPONSORSHIP_CATALOG.values():
            if item.get("category") == "annadanam":
                lines.append(f"• {item['name']}")
                if item.get("temple_fee"):
                    lines.append(f"  – Sponsorship: ${item['temple_fee']}")

        lines.extend([
            "",
            "📞 For coordination and booking:",
            f"• {TEMPLE_INFO['contacts']['catering']}",
            "• Managed by the Annapoorna Committee",
        ])

        return "\n".join(lines)

    # -------------------------------------------------
    # 2️⃣ CATERING / ANNAPOORNA COMMITTEE
    # -------------------------------------------------
    if any(w in q for w in [
        "catering",
        "catering service",
        "catering contact",
        "annapoorna",
        "annapurna",
    ]):
        return (
            "🍽️ ANNADANAM & CATERING SERVICES\n\n"
            "• Catering and Annadanam coordination is handled by:\n"
            f"• {TEMPLE_INFO['contacts']['catering']}\n\n"
            "• Advance notice is required\n"
            "• Coordinated by the Annapoorna Committee"
        )

    # -------------------------------------------------
    # 3️⃣ PRASADAM
    # -------------------------------------------------
    if "prasadam" in q:
        return (
            "🍛 PRASADAM\n\n"
            "• Prasadam is distributed during temple poojas\n"
            "• Availability depends on pooja schedule"
        )

    # -------------------------------------------------
    # 4️⃣ ANNADANAM – GENERAL INFO ONLY (NO DATES)
    # -------------------------------------------------
    if any(w in q for w in ["annadanam", "cafeteria", "food", "lunch", "meal", "annadanam today"]):
        return (
            "🍽️ ANNADANAM\n\n"
            "• Annadanam is distributed on Saturdays & Sundays\n"
            "• Serving time: 12:00 PM – 2:00 PM\n"
            "• Traditional vegetarian meals are served\n"
            "• Managed by the Annapoorna Committee"
        )

    return None

