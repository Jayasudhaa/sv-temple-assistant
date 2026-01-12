##backend/homams_query.py
import datetime
from backend.constants import HOMAMS_DATA,HOMAM_SPONSORSHIP_KEYS
from backend.sponsorship_catalog import SPONSORSHIP_CATALOG


# ============================================================
# HOMAMS DATA (FROM ARJITHA SEVA)
# ============================================================

def homam_list_response() -> str:
    lines = ["🪔 HOMAMS PERFORMED AT THE TEMPLE:\n"]
    for h in HOMAMS_DATA["list"]:
        lines.append(f"• {h}")
    return "\n".join(lines)

def get_homam_sponsorship(q: str) -> str | None:
    q = q.lower()

    for trigger, canonical in HOMAM_SPONSORSHIP_KEYS.items():
        if trigger in q:
            s = SPONSORSHIP_CATALOG.get(canonical)
            if not s:
                return None

            lines = [f"🪔 {s['name']} – SPONSORSHIP", ""]

            if s.get("temple_fee"):
                lines.append(f"• At Temple: ${s['temple_fee']}")
            if s.get("home_fee"):
                lines.append(f"• At Home: ${s['home_fee']}")
            if s.get("group_fee"):
                lines.append(f"• Group Sponsorship: ${s['group_fee']}")

            return "\n".join(lines)

    return None


def handle_homam(q: str, now: datetime) -> str | None:
    q = q.lower()

    # Items handled elsewhere
    if any(w in q for w in ["item", "items", "required", "bring", "samagri", "material"]):
        return None

    if "homam" not in q:
        return None

    # -------------------------
    # SPONSORSHIP (CATALOG-DRIVEN)
    # -------------------------
    if any(w in q for w in ["cost", "price", "sponsorship", "how much", "fee"]):
        sponsorship = get_homam_sponsorship(q)
        if sponsorship:
            return sponsorship

    # -------------------------
    # LIST
    # -------------------------
    if any(w in q for w in ["list", "types", "available"]):
        return homam_list_response()

    # -------------------------
    # SUDARSHANA TIMING (NO PRICE)
    # -------------------------
    if "sudarshana" in q:
        return (
            "🪔 SUDARSHANA HOMAM (SAAMOOHIKA)\n\n"
            "• Performed on 4th Sunday at 11:00 AM\n"
            "• Group homam performed for collective wellbeing\n\n"
        )

    # -------------------------
    # DEFAULT
    # -------------------------
    return (
        "🪔 HOMAM (Fire Ritual)\n\n"
        "• Homams are Vedic fire rituals performed for health, prosperity, and spiritual upliftment\n"
        "• Conducted at the temple or at home (by prior booking)\n"
        "• Sponsorship details are available on request\n\n"
    )
