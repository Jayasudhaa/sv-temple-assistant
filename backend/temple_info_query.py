
##backend/temple_info_query.py 
# 
from backend.constants import GLOBAL_NORMALIZATION_MAP,MONTH_NORMALIZATION_MAP,WEEKLY_EVENTS
from backend.items_catalog_query import ITEMS_REQUIRED
from datetime import datetime,time,date
from backend.federal_holidays import get_federal_holidays
from backend.calender_2026 import CALENDAR_2026
from datetime import datetime, date
from zoneinfo import ZoneInfo
import calendar
from backend.utility import normalize_query
from backend.constants import temple_manager_contact

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

CANONICAL_FESTIVALS = {
    "ugadi": ["ugadi"],
    "ram navami": ["rama navami", "ram navami"],
    "diwali": ["deepavali", "diwali"],
    "sankranti": ["sankranti", "pongal"],
}

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

WEEKLY_SPONSORSHIP = {
    "mahalakshmi abhishekam": (
        "💰 MAHALAKSHMI AMMAVARU ABHISHEKAM – SPONSORSHIP\n\n"
        "• Abhishekam Sponsorship: $116\n"
        "• Vastram Sponsorship: $301\n"
        "  (Includes Abhishekam + temple-provided Vastram)"
        ),

    "ganapati abhishekam": "💰Sponsorship Amount: $51",
    
    "murugan abhishekam": "💰Sponsorship Amount: $51",
    "andal abhishekam": "💰Sponsorship Amount: $116",
    "siva abhishekam": "💰Sponsorship Amount: $51",
    "hanuman abhishekam": "💰Sponsorship Amount: $51",
    "raghavendra swamy abhishekam":"💰Sponsorship Amount: $51",
    
    "sai baba abhishekam": "💰Sponsorship Amount: $51",
    "sudarshana homam": "💰Saamoohika Homam: Sponsorship Amount: $51",

    "venkateswara swamy kalyanam": (
    "💰 SRI VENKATESWARA SWAMY KALYANAM – SPONSORSHIP\n\n"
    "• Kalyanam only: $151\n"
    "• Kalyanam with Vastram: $516\n"
    "  (Temple provides Vastram for Swamy & Ammavaru)"
),
    "venkateswara swamy abhishekam": (
    "💰 SRI VENKATESWARA SWAMY ABHISHEKAM – SPONSORSHIP\n\n"
    "• Abhishekam Sponsorship: $151\n"
    "• Vastram Sponsorship: $1116\n"
    "  (Temple provides Vastram; includes Abhishekam sponsorship)"
), 
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
    
from datetime import datetime, time

def handle_temple_hours(q: str, now: datetime) -> str | None:
    q = q.lower().replace("’", "'")

    if not any(w in q for w in ["open", "close", "hours", "timing", "time"]):
        return None

    today = now.date()
    current_time = now.time()
    is_weekend = now.weekday() >= 5

    # ---------------- HOLIDAY (CALENDAR) ----------------
    holidays = get_federal_holidays(now.year)
    is_holiday = today in holidays
    holiday_name = holidays.get(today)

    # ---------------- FESTIVAL (CALENDAR – SOURCE OF TRUTH) ----------------
    festival_names = []
    if today.year == 2026:
        month = today.strftime("%B").lower()
        day_info = CALENDAR_2026.get(month, {}).get(today.day, {})
        festival_names = day_info.get("festival", [])

    is_festival_day = bool(festival_names)

    # ---------------- FESTIVAL (QUERY INTENT ONLY) ----------------
    is_festival_query = any(w in q for w in [
        "festival",
        "ugadi",
        "yugadi",
        "rama navami",
        "ram navami",
        "diwali",
        "deepavali",
        "sankranti",
        "pongal",
        "navaratri",
        "dussehra",
        "dasara",
        "maha shivaratri",
        "shivaratri",
    ])

    # ---------------- HOLIDAY (QUERY INTENT ONLY) ----------------
    is_holiday_query = any(w in q for w in [
        "holiday",
        "federal holiday",
        "christmas",
        "new year",
        "thanksgiving",
        "independence day",
        "memorial day",
        "labor day",
        "mlk",
        "martin luther king",
        "columbus day",
        "presidents day",
        "president's day",
    ])

    # ---------------- TIME SLOTS ----------------
    full_day_slot = (time(9, 0), time(20, 0))
    weekday_morning = (time(9, 0), time(12, 0))
    weekday_evening = (time(18, 0), time(20, 0))

    def in_range(a, b):
        return a <= current_time <= b

    # ---------------- RESOLVE DAY TYPE (SINGLE SOURCE OF TRUTH) ----------------
    if is_festival_day:
        day_type = "festival"
    elif is_holiday:
        day_type = "federal_holiday"
    elif is_holiday_query:
        day_type = "holiday_query"
    elif is_weekend:
        day_type = "weekend"
    else:
        day_type = "weekday"

    # ---------------- LABEL ----------------
    festival_label = ", ".join(festival_names) if is_festival_day else None

    label = (
        festival_label if day_type == "festival"
        else holiday_name if day_type == "federal_holiday"
        else "Festival Day" if is_festival_query
        else "Federal Holiday" if day_type == "holiday_query"
        else "Weekend" if day_type == "weekend"
        else "Weekday"
    )

    # ---------------- STATUS LOGIC ----------------
    if day_type in ["festival", "federal_holiday", "holiday_query", "weekend"]:
        if in_range(*full_day_slot):
            lines = [
                f"🕉️ TEMPLE STATUS: OPEN Until 8 PM ({label})",
                "",
                "• Hours: 9:00 AM – 8:00 PM",
            ]
        else:
            lines = [
                f"🕉️ TEMPLE STATUS: CLOSED NOW ({label})",
                "",
                "• Hours: 9:00 AM – 8:00 PM",
                "• Next opening: 9:00 AM",
            ]
    else:
        # Weekday split hours
        if in_range(*weekday_morning) or in_range(*weekday_evening):
            lines = [
                f"🕉️ TEMPLE STATUS: OPEN Until 8 PM ({label})",
                "",
                "• Weekday Hours:",
                "  – 9:00 AM – 12:00 PM",
                "  – 6:00 PM – 8:00 PM",
            ]
        else:
            next_open = (
                "9:00 AM today" if current_time < time(9, 0)
                else "6:00 PM today" if current_time < time(18, 0)
                else "9:00 AM tomorrow"
            )
            lines = [
                f"🕉️ TEMPLE STATUS: CLOSED NOW ({label})",
                "",
                "• Weekday Hours:",
                "  – 9:00 AM – 12:00 PM",
                "  – 6:00 PM – 8:00 PM",
                f"• Next opening: {next_open}",
            ]

    # ---------------- FESTIVAL DETAILS ----------------
    if festival_names:
        lines.extend(["", "🎉 Festival(s) Today:"])
        for f in festival_names:
            lines.append(f"• {f}")

   
   

    return "\n".join(lines)

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
    if not any(w in q for w in ["dance", "music", "bhajan", "concert", "performance", "cultural"]):
        return None

    return (
        "🎶 CULTURAL & DEVOTIONAL PROGRAMS\n\n"
        "• Dance, music, bhajans, and cultural programs are welcome\n"
        "• Prior approval and scheduling required\n\n"
        
    )


RAW_MANAGER_APPEND_QUERIES = [
    "abhishekam sponsorship",
    "adyayanotsavam",
    "akshar arambh",
    "aksharabhyasam",
    "andal kalyanam",
    "annadanam sponsorship",
    "annamacharya day",
    "annaprashana",
    "annual sponsorship details",
    "avani avittam",
    "ayush homam cost",
    "bhogi",
    "bhoomi puja",
    "brahmothsavam",
    "chandi homam",
    "cloth offering to god",
    "donate",
    "gaja lakshmi puja",
    "ganapathi abisekam",
    "ganesh chathurthi",
    "ganesh chavithi",
    "gau mata puja",
    "godha kalyanam",
    "godhabhisekam",
    "graha puja",
    "gruhapravesam pooja",
    "half sari function",
    "hanuman abisekam",
    "hanuman vada mala",
    "hindu wedding pooja",
    "hiranya shradham",
    "how do i book a puja",
    "how do i schedule puja",
    "how to book arjitha seva",
    "kanakabhisekam",
    "karthika purnima",
    "lakshmi puja",
    "langa voni",
    "maha shivarathri",
    "mahalakshmi abhisekam",
    "manager contact",
    "meenakshi kalyanam",
    "murugan abisekam",
    "navagraha puja",
    "nischayadartham",
    "nitya archana",
    "padha puja",
    "pumsavana",
    "ram navami",
    "ratha sapthami",
    "rudrabhsekam",
    "sadhabhisekam",
    "sani trayodasi",
    "satyanarayana pooja timing",
    "seemantham",
    "shiva abisekam",
    "shivarathri",
    "sponsorship",
    "subramanya abisekam",
    "sudarshana homam",
    "sumangali prarthanai",
    "swarna pushpa abhisekam",
    "swarna pushpa archana",
    "tulsi kalyanam",
    "upakarma",
    "upanayanam",
    "vaikunta ekadesi",
    "varalakshmi vratham",
    "vastram",
    "vastram sponsorship",
    "vastu puja",
    "venkateswara abhisekam",
    "venkateswara kalyanam",
    "vidyarambam",
    "when is mahalakshmi abhishekam"
]

MANAGER_APPEND_SET = {
    normalize_query(q) for q in RAW_MANAGER_APPEND_QUERIES
}

def append_manager_contact_if_needed(
    user_query: str,
    response: str
) -> str:
    q_norm = normalize_query(user_query)

    if q_norm in MANAGER_APPEND_SET:
        if "TEMPLE MANAGER CONTACT" not in response:
            return response + temple_manager_contact()

    return response
