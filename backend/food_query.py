from datetime import datetime
from backend.temple_info_query import TEMPLE_INFO
from backend.federal_holidays import observe_if_weekend
from backend.sponsorship_catalog import SPONSORSHIP_CATALOG


def handle_food(q: str, now: datetime) -> str | None:
    q = q.lower()
    day = now.strftime("%A")
    is_weekend = observe_if_weekend(now)

    # -------------------------------------------------
    # ANNADANAM / FOOD SPONSORSHIP
    # -------------------------------------------------
    if any(w in q for w in [
        "annadanam sponsor",
        "annadanam sponsorship",
        "sponsor annadanam",
        "annadanam amount",
        "annadanam donation",
        "food sponsorship",
        "anna danam"
    ]):
        lines = [
            "🍽️ ANNADANAM SPONSORSHIP",
            ""
        ]

        for item in SPONSORSHIP_CATALOG.values():
            if item.get("category") == "annadanam":
                lines.append(f"• {item['name']}")
                if item.get("temple_fee"):
                    lines.append(f"  – Sponsorship: ${item['temple_fee']}")

        lines.extend([
            "",
            "📞 For coordination and booking:",
            f"• {TEMPLE_INFO['contacts']['catering']}",
            "• Managed by the Annapoorna Committee"
        ])

        return "\n".join(lines)

    # -------------------------------------------------
    # CATERING / ANNAPOORNA COMMITTEE
    # -------------------------------------------------
    if any(w in q for w in [
        "catering",
        "catering service",
        "catering contact",
        "annapoorna",
        "annapurna"
    ]):
        return (
            "🍽️ ANNADANAM & CATERING SERVICES\n\n"
            "• Catering and Annadanam coordination is handled by:\n"
            f"• {TEMPLE_INFO['contacts']['catering']}\n\n"
            "• Advance notice is required\n"
            "• Coordinated by the Annapoorna Committee"
        )

    # -------------------------------------------------
    # PRASADAM
    # -------------------------------------------------
    if "prasadam" in q:
        return (
            "🍛 PRASADAM\n\n"
            "• Prasadam is available during temple poojas\n"
            "• Availability depends on the pooja schedule"
        )

    # -------------------------------------------------
    # ANNADANAM / CAFETERIA / MEALS
    # -------------------------------------------------
    if any(w in q for w in ["annadanam", "cafeteria", "food", "lunch", "meal"]):
        if is_weekend:
            return (
                "🍽️ ANNADANAM (TEMPLE CAFETERIA)\n\n"
                "• Available today\n"
                "• Serving time: 12:00 PM – 2:00 PM\n"
                "• Traditional vegetarian meals are served"
            )
        else:
            return (
                f"🍽️ ANNADANAM\n\n"
                f"• Not available today ({day})\n"
                "• Served on Saturdays & Sundays only\n"
                "• Serving time: 12:00 PM – 2:00 PM"
            )

    return None
