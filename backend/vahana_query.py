from datetime import datetime
from backend.sponsorship_catalog import SPONSORSHIP_CATALOG


VEHICLE_KEYWORDS = [
    "vahana", "vehicle", "car", "bike", "scooter",
    "auto", "new vehicle", "vehicle pooja",
    "car pooja", "bike pooja", "vehicle blessing"
]


def handle_vahana_pooja(q: str, now: datetime) -> str | None:
    q = q.lower()

    if not any(k in q for k in VEHICLE_KEYWORDS):
        return None

    lines = [
        "🚗 VAHANA POOJA",
        "",
        "📌 Information",
        "• Vahana (Vehicle) Pooja is performed for new or existing vehicles",
        "• Walk-ins are welcome, subject to priest availability",
        "• Archana is included",
        "• Performed during temple hours",
        "",
        "🧺 Items to Bring",
        "• 4 lemons",
        "• 1 coconut",
        "• Fruits",
        "• Flowers",
    ]

    # --------------------------------------------------
    # SPONSORSHIP (EXISTING CATALOG ENTRY)
    # --------------------------------------------------
    sponsorship = SPONSORSHIP_CATALOG.get(
        "vahana_car_pooja_archana_included"
    )

    if sponsorship:
        lines.extend([
            "",
            "💰 Sponsorship",
            f"• Temple: ${sponsorship['temple_fee']}" if sponsorship.get("temple_fee") else "",
            f"• Home: ${sponsorship['home_fee']}" if sponsorship.get("home_fee") else "",
        ])

    return "\n".join(l for l in lines if l.strip())
