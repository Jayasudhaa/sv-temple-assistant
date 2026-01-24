
##backend/temple_info_query.py 
# 
from backend.constants import GLOBAL_NORMALIZATION_MAP,MONTH_NORMALIZATION_MAP,WEEKLY_EVENTS
from backend.items_catalog_query import ITEMS_REQUIRED
from datetime import datetime

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

TEMPLE_VOCAB = set(
    list(GLOBAL_NORMALIZATION_MAP.values())
    + list(MONTH_NORMALIZATION_MAP.values())
    + list(WEEKLY_EVENTS.keys())
    + list(ITEMS_REQUIRED.keys())
    + [
        # Core concepts
        "abhishekam", "homam", "pooja", "panchang",
        "satyanarayana", "kalyanam", "prasadam",
        "poornima", "amavasya", "nakshatra", "tithi",
        "venkateswara", "siva", "murugan", "ganapati",
        "hanuman", "sai baba", "raghavendra",
        "today", "tomorrow", "weekend",
        "events", "schedule", "timing", "hours",
    ]
)

TEMPLE_INFO = {
    "address": "1495 South Ridge Road, Castle Rock, Colorado 80104",
    "Temple_Manager": "303-898-5514",
    "Temple_phone" : "303-660-9555",
    "email": "manager@svtempleco.org",
    "website": "www.svtempleco.org",
    
    # TEMPLE TIMINGS
    "hours": {
        "weekday": "Weekdays (Monday-Friday): 9:00 AM - 12:00 PM and 6:00 PM - 8:00 PM",
        "weekend": "Weekends and Holidays: 9:00 AM - 8:00 PM",
        "cafeteria": "Cafeteria: Weekends only (Saturday & Sunday) 12:00 PM - 2:00 PM"
    },
    
    # LEADERSHIP & COMMITTEES
    "contacts": {
        "chairman": "Saiganesh Rajamani - 303-941-4166",
        "president": "Sri. Satyanarayana Velagapudi (Executive Committee President)",
        "manager": "Sri. Nandu Sankaran - 303-898-5514 or manager@svtempleco.org",
        "catering": "Annapoorna Committee Chair Smt. Swetha Sarvabhotla - 537-462-6167"
    },
    
    # TEMPLE COMMITTEES
    "committees": {
        "annapoorna": "Annapoorna Committee - Smt. Swetha Sarvabhotla (Chair)",
        "religious": "Religious Committee - Sri. Raju Dandu (Chair)",
        "finance": "Finance Committee - Sri. Dileep Kumar Kadirimangalam (Chair)",
        "executive": "Executive Committee - Sri. Satyanarayana Velagapudi (President)",
        "web_communications": "Web & Communications Committee - Smt. Suneeja Ankana (Chair)",
        "multimedia": "Multi Media Committee - Sri. Srinivasa Katamaneni (Chair)",
        "facilities": "Facilities Committee - Sri. Balu Gullepalli (Chair)",
        "education_cultural": "Education & Cultural Committee - Sri. Krishna Madhavan (Chair)",
        "security": "Security Committee - Sri. Muthukumarappan Ramurthy (Chair)"
    }
}

LIFE_EVENT_KEYWORDS = [
    "sashtiapdhapoorthi",
    "seemantham",
    "sadhabhisekam",
    "ritu kala samhara",
    "upanayanam",
    "pinda dhan",
    "mundan",
    "antyeshti",
    "karnavedha",
    "chudakarana",
    "annaprashana",
    "nishkramana",
    "namakarana",
    "jatakarma",
    "simantonnayana",
    "pumsavana",
    "garbadhana",
    "aksharabhyasam",
    "nischayadartham",
    "nischayadhartham",
    "engagement",
    "beema ratha santhi",
    "bima ratha shanthi",
    "sashtiabdapoorthi",
    "shashtiapthapoorthi",
    "shradha",
    "shraddha",
    "annual shraddha",
    "upakarma",
    "avani avittam",
    "brahmothsavam",
    "brahmotsavam",
    "adyayanotsavam",
    "meenakshi kalyanam",
    "rudram",
    "life event",
    "special ceremony",
    "hindu Wedding",
    "engagement ceremony",
    "gruhapravesam",
    "namakaranam",
    "half saree",
    "first year birthday",
    "mundan",
    "vivaha",
    "nishkramana",
 ]

def handle_location(q: str, now: datetime) -> str | None:
    if not any(w in q for w in ["address", "location", "where is", "directions"]):
        return None

    return (
        "📍 SRI VENKATESWARA TEMPLE – LOCATION\n\n"
        f"• Address: {TEMPLE_INFO['address']}\n"
        "• City: Castle Rock, Colorado\n"
        "• Parking available on-site\n\n"
        
    )
def handle_vedic_recitation(q: str, now: datetime) -> str | None:
    return (
        "🪔 VEDIC RECITATIONS & CHANTING\n\n"
        "• Sukthams, Sahasranamams, and Nama Sankeerthanams "
        "are priest-led services based on availability and temple schedule\n"
        "• Please contact the Temple Manager for timing, booking, or participation details\n\n"
        
    )
    


def handle_contacts(q: str, now: datetime) -> str | None:
    q = q.lower()

    if "chairman" in q:
        return f"• Chairman: {TEMPLE_INFO['contacts']['chairman']}"

    if "president" in q:
        return f"• President: {TEMPLE_INFO['contacts']['president']}"

    if "manager" in q:
        return f"• Manager: {TEMPLE_INFO['contacts']['manager']}"

    if "catering" in q:
        return f"• Catering: {TEMPLE_INFO['contacts']['catering']}"

    if any(w in q for w in ["contact", "phone", "email", "call"]):
        return (
            "📞 TEMPLE CONTACTS\n\n"
            f"• Chairman: {TEMPLE_INFO['contacts']['chairman']}\n"
            f"• President: {TEMPLE_INFO['contacts']['president']}\n"
            f"• Manager: {TEMPLE_INFO['contacts']['manager']}\n"
            f"• Catering: {TEMPLE_INFO['contacts']['catering']}"
        )

    return None


def handle_committee_queries(q: str, now: datetime) -> str | None:
    q = q.lower()

    # Specific committee lookup
    for key, value in TEMPLE_INFO["committees"].items():
        if key.replace("_", " ") in q:
            return f"• {value}"

    # General committee listing
    if any(w in q for w in ["committee", "committees", "board", "trustee", "leadership"]):
        lines = ["🏛️ TEMPLE COMMITTEES", ""]
        for c in TEMPLE_INFO["committees"].values():
            lines.append(f"• {c}")
        return "\n".join(lines)

    return None

def handle_cultural_programs(q: str, now: datetime) -> str | None:
    print("inside cultural",q)
    if not any(w in q for w in ["dance", "music", "bhajan", "concert", "performance", "cultural","singing", "cultural programmes","cultural programs"]):
        return None

    return (
        "🎶 CULTURAL & DEVOTIONAL PROGRAMS\n\n"
        "• Dance, music, bhajans, and cultural programs are welcome\n"
        "• Prior approval and scheduling required\n\n"
        
    )





