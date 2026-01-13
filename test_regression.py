import pytest
from datetime import datetime
from zoneinfo import ZoneInfo

from backend.ask_temple import answer_user

message_ts = int(datetime.now(ZoneInfo("America/Denver")).timestamp())


# =========================================================
# ALL ABHISHEKAM QUERY VARIANTS (REAL USER LANGUAGE)
# =========================================================

ABHISHEKAM_QUERIES = [

    # -------------------------------------------------
    # GENERIC
    # -------------------------------------------------
    "abhishekam",
    "abhishekam schedule",
    "when is abhishekam",
    "temple abhishekam",
    "list abhishekams",

    # -------------------------------------------------
    # DEITY-SPECIFIC
    # -------------------------------------------------
    "siva abhishekam",
    "shiva abhishekam",
    "venkateswara abhishekam",
    "balaji abhishekam",
    "tirupati abhishekam",
    "andal abhishekam",
    "mahalakshmi abhishekam",
    "hanuman abhishekam",
    "murugan abhishekam",
    "ganapati abhishekam",
    "sai baba abhishekam",
    "raghavendra swamy abhishekam",

    # -------------------------------------------------
    # TIME-RELATIVE
    # -------------------------------------------------
    "abhishekam this week",
    "abhishekam next week",
    "abhishekam last week",
    "abhishekam this month",
    "abhishekam next month",
    "abhishekam in february",
    "abhishekam after 4 months",

    # -------------------------------------------------
    # SPONSORSHIP
    # -------------------------------------------------
    "abhishekam sponsorship",
    "abhishekam cost",
    "how much is abhishekam",
    "abhishekam fee at temple",
    "abhishekam fee at home",

    # -------------------------------------------------
    # MOOLA / TYPE
    # -------------------------------------------------
    "moola murthy abhishekam",
    "individual abhishekam",
    "saamoohika abhishekam",

    # -------------------------------------------------
    # VASTRA SAMARPANAM
    # -------------------------------------------------
    "venkateswara abhishekam vastram",
    "andal abhishekam vastram",
    "mahalakshmi vastram",
    "vastra samarpanam andal",

    # -------------------------------------------------
    # COMBINED NATURAL LANGUAGE
    # -------------------------------------------------
    "when is siva abhishekam and how much does it cost",
    "andal abhishekam next month sponsorship",
    "venkateswara abhishekam with vastram",
    "is abhishekam happening this saturday",

    # -------------------------------------------------
    # SPELLING / FUZZY
    # -------------------------------------------------
    "abishekam",
    "abishkam",
    "abishegam",

    # -------------------------------------------------
    # EDGE / UNKNOWN
    # -------------------------------------------------
    "krishna abhishekam",
    "unknown deity abhishekam",

     # ---------------- PAST ----------------
    "siva abhishekam last week",
    "abhishekam yesterday",
    "abhishekam in december 2025",
    "was there any abhishekam last month",

    # ---------------- PRESENT ----------------
    "abhishekam today",
    "is there abhishekam this week",
    "any abhishekam this month",

    # ---------------- FUTURE ----------------
    "siva abhishekam next week",
    "abhishekam next month",
    "abhishekam in march",
    "abhishekam in april 2026",
    "when is abhishekam in may",
    "venkateswara abhishekam in june",
    "siva abhishekam in july",
    "abhishekam in august",
    "abhishekam in september",
    "abhishekam in october",
    "abhishekam in november",
    "abhishekam in december",
    "Abhishekam sponsorship",
     "Ganapathi Abisekam",
     "Venkateswara Abhisekam",
     "Venkateswara Kalyanam",

    # ---------------- EXPLICIT DATE ----------------
    "siva abhishekam on jan 10",
    "abhishekam on feb 14 2026",
    "is there abhishekam on march 1st",
    "any abhishekam on april 5",

    # Generic
    "kalyanam",
    "kalyanam schedule",
    "when is kalyanam",
    "temple kalyanam",

    # Relative time
    "kalyanam today",
    "kalyanam this week",
    "kalyanam next week",
    "kalyanam this month",
    "kalyanam next month",

    # Month specific
    "kalyanam in february",
    "kalyanam in march",
    "kalyanam in april 2026",
    "venkateswara kalyanam in may",
    "srinivasa kalyanam in june",

    # Explicit date
    "kalyanam on jan 10",
    "kalyanam on feb 14 2026",
    "is there kalyanam on march 1st",

    "kalyanam sponsorship",
    "kalyanam sponsorship details",
    "kalyanam cost",
    "kalyanam price",
    "how much is kalyanam",
    "venkateswara kalyanam sponsorship",
    "srinivasa kalyanam sponsorship",
    "kalyanam temple fee",
    "kalyanam home sponsorship",

    "when is venkateswara kalyanam and how much does it cost",
    "kalyanam next month sponsorship",
    "tell me about kalyanam at the temple",
    "is there any upcoming kalyanam",
    "kalyanam dates and sponsorship",
    "kalyanam happening this saturday",
    "Andal Kalyanam",

     # Typos
    "kalyanam",
    "kalynam",
    "kalyanem",

    # Unknown deity
    "krishna kalyanam",
    "unknown deity kalyanam",
    
    # Ambiguous
    "special kalyanam",
    "any big kalyanam coming up",
    "Cloth offering to god",

    # Stress / vague
    "tell me everything about kalyanam",

    #TempleTimings
    "Is the Temple Open Today (Holiday)?",

    #festivals

    "Aadi Krithigai",
    "Adyayanotsavam",
    "Akshar Arambh",
    "Aksharabhyasam",
    "Ashtami",
    "Annamacharya Day",
    "Avani Avittam",
    "Beema Ratha Santhi",
    "Bheeshma Ekadeshi",
    "Bhogi",
    "Chaath Puja",
    "Christmas",
    "Deepavali",
    "Diwali",
    "Durga Ashtami",
    "Dusshera",
    "Dwadhashi",
    "English new year",
    "Ganesh Chathurthi",
    "Godha Kalyanam",
    "Gokulashtami",
    "Guru Purnima",

    #lifeevents
    "Annaprashana",
    "Antyeshti",
    "Bhoomi Puja",
    "Chudakarana",
    "Graha Puja",
    "Garbadhana",

    #address
    "Address",
    
    "Aksharabhyasam items",
    "Amavasya dates",
    "Amma",
    "Ammavaru",
    
    "Annadanam sponsorship",
    "Annadanam timing",
    
    #today
    "Any Special Events Today",
    
    
    "Appa",
    "BalaVihar",
    "Bhagavad Gita Class",
    "Bhajans at temple",
    "Brahmothsavam",

    #homam
    "Ayush Homam cost",    
    "Chandi Homam",
    "homam",
    "homams",
    "list homams",
    "homam list",
    "what homams are performed",
    "available homams",
    "ayush homam",
    "chandi homam",
    "sudarshana homam",
    "navagraha homam",
    "lakshmi homam",
    "ganapathi homam",
    "venkateswara homam",
    "rudra homam",
    "mrutyunjaya homam",
    "dhanvantari homam",
    "saraswati homam",
    "ayush homam cost",
    "ayush homam sponsorship",
    "how much is ayush homam",

    "chandi homam cost",
    "chandi homam sponsorship",
    "price for chandi homam",

    "sudarshana homam sponsorship",
    "sudarshana homam cost",
    "group homam sponsorship",
    "saamoohika homam sponsorship",

    "navagraha homam cost",
    "homam price at temple",
    "homam price at home",

    # --------------------------------------------------
    # TIME / SCHEDULE
    # --------------------------------------------------
    "when is sudarshana homam",
    "sudarshana homam timing",
    "is sudarshana homam this week",
    "homam this month",
    "homam next month",

    # --------------------------------------------------
    # COMBINED NATURAL LANGUAGE
    # --------------------------------------------------
    "when is sudarshana homam and how much does it cost",
    "chandi homam sponsorship details",
    "ayush homam at home cost",

     # --------------------------------------------------
    # SPELLING / FUZZY
    # --------------------------------------------------
    "sudarshan homam",
    "sudharshana homam",
    "ayus homam",
    "chandhi homam",

    # --------------------------------------------------
    # ITEMS (MUST NOT BE HANDLED HERE)
    # --------------------------------------------------
    "homam items",
    "items for homam",
    "homam samagri",
    "what to bring for homam",

    # --------------------------------------------------
    # UNKNOWN / EDGE
    # --------------------------------------------------
    "krishna homam",
    "unknown homam",
    "special homam",
    "any powerful homam",

    # --------------------------------------------------
    # NEGATIVE
    # --------------------------------------------------
    "homam story",
    "homam significance",
    "why do homam",

    #temple_info
    "Board of Trustees",
    "Cafeteria timing",
    "Calendar",
    "Catering contact",
    "Catering service contact",
    "Cultural Prograns",
    "Daily pooja schedule",
    "Dance performance at temple",
    "Founding Members",

    #panchang

    "Dec 1 panchang",
    
    "Diwali story",
    "Donate",
   
    "email",
   
    "Events 2026",
    "Events January 2026",
    "Events Today",

    "Festival",
    "Festivals",
       
    "Hanuman Abisekam",
    "Hindu wedding pooja",
    "Holi",
    "Holiday",
    "Holiday hours",
    "How do I book a puja",
    "Is annadanam available today?",
    "Is the temple open today?",
    "Janmashtami",
    "Kanakabhisekam",
    "Karthigai Deepam",
    "Krishna Jayanthi",
    "Lakshmi Puja",
    "Lalitha Sahasranamam",
    "List arjitha sevas",
    "List of homams",
    "Maha Shivarathri",
    "Mahalakshmi Abhisekam",
    "Manager contact",
    "Martin Luther Day",
    "Meenakshi Kalyanam",
    "Monthly pooja schedule",
    "Murugan Abisekam",
    "Naalaayira Divya Prabhandham",
    "Nama Sankeerthanam",
    "Navagraha Puja",
    "Navarathri",
    "Nitya Archana",
    "Onam",
    "Pongal",
    "Pradhosham",
    "Ram Navami",
    "Rudrabhsekam",
    "Sahasranamam",
    "Satyanarayana pooja timing",
    "Shiva Abisekam",
    "Shivarathri",
    "Sri Venkateswra Temple of Colorado",
    "Subramanya Abisekam",
    "Suprabatham",
    "Tamil New year",
    "Temple address",
    "Temple Calendar",
    "Temple hours / timings",
    "Temple phone number",
    "Thanksgiving",
    "Today panchang",
    "Today's Events",
    "Tulsi Kalyanam",
    "Ugadi",
    "Upanayanam",
    "Vahana Puja",
    "Vaikunta Ekadesi",
    "Varalakshmi Vratham",
    
    "Vidyarambam",
    "Vijaya Dhashami",
    "Vinayakar Chathurthi",
    "Vishnu Sahasranamam",
    "Volunteer Appreciation",
    "Website",
    "Weekday hours",
    "Weekend Hours",
    "What is arjitha seva?",
    "What time does the temple open?",
    "When does the temple close?",
    "Where is the temple located?",
    "Who is the chairman?",
    "Who is the president?",

    #items
    "items for aksharabhyasam",
    "aksharabhyasam samagri",
    "akshara abhyasam items",
    "vidyarambham items",
    "vidya arambham samagri",
    "first writing ceremony items",
    "akshara abhyasam items",
    "vidyarambham items",
    "vidya arambham samagri",
    "first writing ceremony items",
    "items for satyanarayana pooja",
    "satyanarayana samagri",
    "what to bring for satyanarayana vratham",
    "homam items",
    "items for any homam",
    "sudarshana homam items",
    "items",
    "samagri",
    "what items should I bring",
    "materials",

     # ---------------- BASIC ----------------
    "satyanarayana pooja",
    "satya narayana pooja",
    "satyanarayan pooja",
    "satyanarayana swamy pooja",
    "satyanarayana vratham",

    # ---------------- TIMING ----------------
    "when is satyanarayana pooja",
    "satyanarayana pooja timing",
    "satyanarayana pooja time",

    # ---------------- SPONSORSHIP ----------------
    "satyanarayana pooja sponsorship",
    "satyanarayana pooja cost",
    "how much is satyanarayana pooja",
    "satyanarayana pooja fee at temple",
    "satyanarayana pooja fee at home",
    "saamoohika satyanarayana pooja",

    # ---------------- ITEMS ----------------
    "satyanarayana pooja items",
    "items for satyanarayana pooja",
    "satyanarayana samagri",
    "what to bring for satyanarayana vratham",
    "materials required for satyanarayana pooja",

    # ---------------- SPELLING / FUZZY ----------------
    "satya narayan pooja",
    "sathyanarayana pooja",
    "satyanarayanam pooja",

    #manager append
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
    "mahalakshmi abhishekam"
 
]

def assert_not_fallback(response: str):
    assert "I don’t have specific information" not in response
    assert "No special events scheduled" not in response


def assert_contains_any(response: str, keywords: list[str]):
    lowered = response.lower()
    assert any(k in lowered for k in keywords), f"Expected one of {keywords}"


def assert_not_contains(response: str, forbidden: list[str]):
    lowered = response.lower()
    for f in forbidden:
        assert f not in lowered, f"Forbidden phrase found: {f}"

# =========================================================
# TEST
# =========================================================

@pytest.mark.parametrize("query", ABHISHEKAM_QUERIES)
def test_abhishekam_bot_responses(query):
    response = answer_user(query, message_ts=message_ts)

    print("\n" + "=" * 90)
    print(f"QUERY : {query}")
    print("-" * 90)
    print("BOT RESPONSE:\n")
    print(response)
    print("=" * 90)

    # Only ensure bot doesn't crash
    assert response is not None

# =========================================================
# ASSERTION HELPERS
# =========================================================

def assert_not_empty(resp: str):
    assert resp and resp.strip(), "Empty response returned"


def assert_not_generic_fallback(resp: str):
    forbidden = [
        "i don’t have specific information",
        "i don't have specific information",
        "unable to find",
    ]
    for f in forbidden:
        assert f not in resp.lower(), f"Generic fallback used: {f}"


def assert_contains_any(resp: str, words: list[str]):
    text = resp.lower()
    assert any(w in text for w in words), f"Expected one of {words}"


# =========================================================
# DOMAIN ASSERTIONS
# =========================================================

def assert_abhishekam(resp: str):
    assert_contains_any(resp, ["abhishekam"])
    assert_not_generic_fallback(resp)


def assert_kalyanam(resp: str):
    assert_contains_any(resp, ["kalyanam"])
    assert_not_generic_fallback(resp)


def assert_satyanarayana(resp: str):
    assert_contains_any(resp, ["satyanarayana"])
    assert "temple status" not in resp.lower()


def assert_events(resp: str):
    if "no special events" in resp.lower():
        # Must include daily pooja or panchang fallback
        assert_contains_any(resp, ["daily pooja", "panchang"])
    else:
        assert_contains_any(resp, ["event", "pooja", "festival"])


def assert_food(resp: str):
    assert_contains_any(resp, ["annadanam", "food"])


def assert_items(resp: str):
    assert_contains_any(resp, ["items", "samagri", "bring"])


def assert_hours(resp: str):
    assert_contains_any(resp, ["temple status", "hours", "open", "closed"])


# =========================================================
# MAIN TEST
# =========================================================

@pytest.mark.parametrize("query", ABHISHEKAM_QUERIES)
def test_bot_responses(query):
    resp = answer_user(query, message_ts=message_ts)

    print("\n" + "=" * 100)
    print("QUERY:", query)
    print("-" * 100)
    print(resp)
    print("=" * 100)

    assert_not_empty(resp)

    q = query.lower()

    if "abhishekam" in q or "abishek" in q:
        assert_abhishekam(resp)

    elif "kalyanam" in q:
        assert_kalyanam(resp)

    elif "satyanarayana" in q:
        assert_satyanarayana(resp)

    elif any(w in q for w in ["event", "events", "happening", "activities"]):
        assert_events(resp)

    elif any(w in q for w in ["annadanam", "food", "cafeteria"]):
        assert_food(resp)

    elif any(w in q for w in ["item", "samagri", "bring"]):
        assert_items(resp)

    elif any(w in q for w in ["open", "close", "hours", "timing"]):
        if "satyanarayana" not in q:
            assert_hours(resp)

    else:
        # Unknown queries must still not hard-fail
        assert_not_generic_fallback(resp)
