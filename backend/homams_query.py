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

    print("[DEBUG] get_homam_sponsorship scanning:", q)
    if "sudarshana" in q or "sudarshan" in q:
        return (
            "🪔 SUDARSHANA HOMAM\n\n"
            "📅 TEMPLE (SAAMOOHIKA):\n"
            "• Happens every 4th Sunday at the Temple\n"
            "• Sponsorship: $116\n\n"
            "👤 INDIVIDUAL (BY APPOINTMENT):\n"
            "• At Temple: $151\n"
            "• At Home: $251\n\n"
            "📌 Advance booking required"
        )


    # -------------------------------------------------
    # 1️⃣ SPECIFIC HOMAM MATCH
    # -------------------------------------------------
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

            return "\n".join(lines)

    # -------------------------------------------------
    # 2️⃣ GENERIC HOMAM COST (fallback)
    # -------------------------------------------------
    if "homam" in q and any(w in q for w in ["cost", "price", "fee", "sponsorship"]):
        lines = [
            "🪔 HOMAM SPONSORSHIP DETAILS",
            ""
        ]

        found = False
        for item in SPONSORSHIP_CATALOG.values():
            if item.get("category") == "homam":
                found = True
                lines.append(f"• {item['name']}")
                if item.get("temple_fee"):
                    lines.append(f"  – At Temple: ${item['temple_fee']}")
                if item.get("home_fee"):
                    lines.append(f"  – At Home: ${item['home_fee']}")

        if found:
            return "\n".join(lines)

    return None



def handle_homam(q: str, now: datetime) -> str | None:
    q = q.lower()

    # ✅ COST / SPONSORSHIP FIRST
    sponsorship = get_homam_sponsorship(q)
    if sponsorship:
        return sponsorship

    # ❌ generic homam text only if no pricing intent
    return (
        "🪔 HOMAM (Fire Ritual)\n"
        "• Homams are Vedic fire rituals performed for health, prosperity, and spiritual upliftment\n"
        "• Conducted at the temple or at home (by prior booking)\n"
        "• Sponsorship details are available on request"
    )
