# backend/daily_pooja_query.py
from datetime import datetime, time
from backend.constants import DAILY_SCHEDULE

def handle_daily_pooja(q: str, now: datetime) -> str | None:
    q = q.lower()

    is_today_query = any(w in q for w in [
        "today", "now", "this morning", "happening"
    ])

    is_suprabhata_query = "suprabhata" in q

    suprabhata_time = time(9, 0)

    lines = []

    # --------------------------------------------------
    # SUPRABHATA SEVA (AUTO for TODAY or EXPLICIT QUERY)
    # --------------------------------------------------
    if is_today_query or is_suprabhata_query:
        if now.time() < suprabhata_time:
            status = "UPCOMING"
        elif now.time() >= suprabhata_time:
            status = "COMPLETED"

        lines.extend([
            "🪔 SRI VENKATESWARA SUPRABHATA SEVA",
            f"• Time: 9:00 AM",
            f"• Status: {status}",
            "• Performed daily at the temple",
            "• Marks the ceremonial awakening of Lord Venkateswara",
            ""
        ])

        # If user asked ONLY suprabhata, stop here
        if is_suprabhata_query and not is_today_query:
            return "\n".join(lines)

    # --------------------------------------------------
    # FULL DAILY POOJA SCHEDULE
    # --------------------------------------------------
    if "daily" in q and "pooja" in q or is_today_query:
        lines.append("📿 DAILY POOJA SCHEDULE")
        for s in DAILY_SCHEDULE:
            lines.append(f"• {s}")
        lines.append("")

    return "\n".join(lines) if lines else None
