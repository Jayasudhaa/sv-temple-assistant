from datetime import datetime
from backend.constants import ARJITHA_TRIGGER_KEYWORDS, ARJITHA_FEES


def handle_arjitha_seva(q: str, now: datetime) -> str | None:
    q = q.lower().strip()

    if not any(k in q for k in ARJITHA_TRIGGER_KEYWORDS):
        return None

    link = "https://svtempleco.org/Home/ArjithaSeva.html"

    # -----------------------------
    # Build fee list lines (NO placeholders)
    # -----------------------------
    lines = []
    for i, (desc, fees) in enumerate(ARJITHA_FEES.items(), start=1):
        parts = []

        temple_fee = fees.get("temple")
        home_fee = fees.get("home")

        if temple_fee is not None:
            parts.append(f"Temple: ${temple_fee:,} sponsorship")

        if home_fee is not None:
            parts.append(f"Home: ${home_fee:,} sponsorship")

        if parts:
            lines.append(f"• {i}) {desc} — " + " | ".join(parts))
        else:
            lines.append(f"• {i}) {desc}")

    # -----------------------------
    # 1) WHAT IS / MEANING
    # -----------------------------
    if any(w in q for w in ["what is", "meaning", "explain"]):
        return (
            "🪔 ARJITHA SEVA\n\n"
            "• Arjitha Seva is a special priest-performed service requested by individual devotees\n"
            "• Includes Abhishekam, Archana, Homam, Vrathams, and life-event ceremonies\n\n"
            f"🔗 Full list & sponsorship details: {link}"
        )

    # -----------------------------
    # 3) DEFAULT: SHOW FULL LIST
    # -----------------------------
    return (
        "🪔 ARJITHA / PRIVATE POOJA SERVICES (Effective 04/01/2025)\n"
        "• Sponsorship Fee List\n\n"
        + "\n".join(lines)
        + f"\n\n🔗 Official page: {link}"
    )
