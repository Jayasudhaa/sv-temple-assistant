##backend/constants.py
# ============================================================
# WEEKLY ABHISHEKAM SCHEDULE (EXACT FROM TEMPLE)
# ============================================================

WEEKLY_EVENTS = {
    "venkateswara swamy abhishekam":
        "1st Saturday 11:00 AM – Sri Venkateswara Swamy Abhishekam (Moola Murthy)",

    "venkateswara swamy kalyanam":
        "2nd Saturday 11:00 AM – Sri Venkateswara Swamy Kalyanam",

    "siva abhishekam":
        "1st Sunday 11:00 AM – Sri Siva Abhishekam",

    "murugan abhishekam":
        "2nd Sunday 11:00 AM – Sri Murugan Abhishekam",

    "andal abhishekam":
        "3rd Friday 11:00 AM – Sri Andal Abhishekam",

    "mahalakshmi abhishekam":
        "3rd Saturday 11:00 AM – Sri Mahalakshmi Abhishekam",

    "hanuman abhishekam":
        "4th Saturday 11:00 AM – Sri Hanuman Abhishekam",

    "ganapati abhishekam":
        "2nd Sunday 11:00 AM – Sri Ganapati Abhishekam",

    "raghavendra swamy abhishekam":
        "3rd Sunday 11:00 AM – Sri Raghavendra Swamy Abhishekam",

    "sai baba abhishekam":
        "4th Sunday 11:00 AM – Sri Sai Baba Abhishekam",


}


CANONICAL_WEEKLY_KEYS = {
    # -----------------------------
    # VENKATESWARA
    # -----------------------------
    "venkateswara swamy abhishekam": "venkateswara swamy abhishekam",
    "venkateswara abhishekam": "venkateswara swamy abhishekam",
    "venkateshwara abhishekam": "venkateswara swamy abhishekam",

    # -----------------------------
    # SIVA
    # -----------------------------
    "siva abhishekam": "siva abhishekam",
   
    # -----------------------------
    # MURUGAN / SUBRAMANYA
    # -----------------------------
    "murugan abhishekam": "murugan abhishekam",
    "subramanya abhishekam": "murugan abhishekam",

    # -----------------------------
    # ANDAL
    # -----------------------------
    "andal abhishekam": "andal abhishekam",

    # -----------------------------
    # MAHALAKSHMI
    # -----------------------------
    "mahalakshmi abhishekam": "mahalakshmi abhishekam",
    "mahalakshmi ammavaru abhishekam": "mahalakshmi abhishekam",
    "ammavaru abhishekam": "mahalakshmi abhishekam",

    # -----------------------------
    # HANUMAN
    # -----------------------------
    "hanuman abhishekam": "hanuman abhishekam",
    "ganapati abhishekam": "ganapati abhishekam",
    
    # RAGHAVENDRA
    "raghavendra swamy abhishekam": "raghavendra swamy abhishekam",
    
    # SAI BABA
    "sai baba abhishekam": "sai baba abhishekam", 

    # -----------------------------
    # ANDAL / GODA
    # -----------------------------
    "andal abhishekam": "andal abhishekam",
    "goda abhishekam": "andal abhishekam",

    # -----------------------------
    # TULASI
    # -----------------------------
    "tulasi abhishekam": "tulasi abhishekam",
    "tulsi abhishekam": "tulasi abhishekam",

    # -----------------------------
    # MEENAKSHI
    # -----------------------------
    "meenakshi abhishekam": "meenakshi abhishekam",
    "meenkashi abhishekam": "meenakshi abhishekam",


}

DISPLAY_WEEKLY_NAMES = {
    "siva abhishekam": "Sri Siva Abhishekam",
    "murugan abhishekam": "Sri Murugan Abhishekam",
    "andal abhishekam": "Sri Andal Abhishekam",
    "mahalakshmi abhishekam": "Sri Mahalakshmi Abhishekam",
    "hanuman abhishekam": "Sri Hanuman Abhishekam",
    "venkateswara swamy abhishekam": "Sri Venkateswara Swamy Abhishekam",
    "ganapati abhishekam": "Sri Ganapati Abhishekam",
    "raghavendra swamy abhishekam": "Sri Raghavendra Swamy Abhishekam",
    "sai baba abhishekam": "Sri Sai Baba Abhishekam",
    "venkateswara swamy kalyanam": "Sri Venkateswara Swamy Kalyanam",
    "andal abhishekam": "Sri Goda Devi (Andal) Abhishekam",
    "tulasi abhishekam": "Sri Tulasi Devi Abhishekam",
    "meenakshi abhishekam": "Sri Meenakshi Devi Abhishekam",
}

MONTH_NORMALIZATION_MAP = {
    "jan": "january",
    "jan.": "january",
    "january": "january",

    "feb": "february",
    "feb.": "february",
    "february": "february",

    "mar": "march",
    "mar.": " march",
    "march": " march",

    "apr": "april",
    "apr.": " april",
    "april": " april",

    "jun": "june",
    "jun.": "june",
    "june": "june",

    "jul ": " july",
    "jul.": " july",
    "july ": " july ",

    "aug ": " august",
    "aug.": " august",
    "august ": " august",

    "sep": " september",
    "sept": " september",
    "sep.": " september",
    "september ": " september",

    "oct": "october",
    "oct.": "october",
    "october": "october",

    "nov": "november",
    "nov.": "november",
    "november": "november",

    "dec": "december",
    "dec.": "december",
    "december": "december",
}

DAY_NORMALIZATION_MAP = {
    "mon": "monday",
    "mon.": "monday",
    "monday": "monday",

    "tue": "tuesday",
    "tues": "tuesday",
    "tue.": "tuesday",
    "tues.": "tuesday",
    "tuesday": "tuesday",

    "wed": "wednesday",
    "wed.": "wednesday",
    "wednesday": "wednesday",

    "thu": "thursday",
    "thur": "thursday",
    "thurs": "thursday",
    "thu.": "thursday",
    "thursday": "thursday",

    "fri": "friday",
    "fri.": "friday",
    "friday": "friday",

    "sat": "saturday",
    "sat.": "saturday",
    "saturday": "saturday",

    "sun": "sunday",
    "sun.": "sunday",
    "sunday": "sunday",
}


CANONICAL_INTENTS = {
    # -----------------------------
    # VIDYARAMBHAM
    # -----------------------------
    "aksharabhyasam": [
        "vidyarambam",
        "vidyarambham",
        "akshar arambh",
        "akshar arambham",
        "aksharabhyasam",
        "akshara abhyasam",
    ],

    # -----------------------------
    # MAHA SHIVARATRIhandled 
    # -----------------------------
    "mahashivaratri": [
        "maha shivaratri",
        "mahashivaratri",
        "shivaratri",
        "shivarathri",
        "shiva ratri",
    ],

    # -----------------------------
    # PONGAL / SANKRANTHI
    # -----------------------------
    "pongal": [
        "pongal",
        "sankranthi",
        "sankranti",
        "shankranthi",
        "makara sankranthi",
    ],
}

DAILY_SCHEDULE = [
    "09:00 AM – Sri Venkateswara Suprabhata Seva",
    "10:00 AM – Sri Venkateswara Nitya Archana",
    "06:30 PM – Archana and Deeparadhana",
    "07:30 PM – Ekantha Seva"

]

MONTHLY_SCHEDULE = [
    "1st Saturday – Sri Venkateswara Abhishekam",
    "1st Sunday – Siva Abhishekam",
    "2nd Saturday – Sri Venkateswara Kalyanam",
    "2nd Sunday – Sri Ganapthi/Murugan Abhishekam",
    "1st Saturday – Sri Venkateswara Abhishekam",
    "3rd Friday – Sri Andal Abhishekam",
    "3rd Saturday – Sri Mahalakshmi Abhishekam",
    "4th Saturday – Sri Hanuman Abhishekam",
    "4th Sunday – Sudarshana Homam",
]

GLOBAL_NORMALIZATION_MAP = {

    **MONTH_NORMALIZATION_MAP,
    **DAY_NORMALIZATION_MAP,

    # Abhishekam spellings
    "abisekam": "abhishekam",
    "abisegam": "abhishekam",
    "abhisheka": "abhishekam",

    # Deity spellings
    "venkateshwar": "venkateswara",
    "venkateshwara": "venkateswara",
    "ganapathy": "ganapati",
    "shiva": "siva",
    "shiv": "siva",

    # Lunar spellings
    "purnima": "poornima",
    "pournami": "poornima",

    # Festival spellings
    "shivarathri": "shivaratri",
    "sankranthi": "pongal",
    "shankranthi": "pongal",

    # ✅ GANAPATI
    "ganapathi": "ganapati",
    "vinayaka": "ganapati",
    "pillaiyar": "ganapati",
    "ganesha" : "ganapati",

    # ✅ SAI BABA
    "saibaba": "sai baba",
    "shiridi sai": "sai baba",
    "shirdi sai": "sai baba",

    # ✅ RAGHAVENDRA
    "raghavendra": "raghavendra swamy",
    "ragavendra": "raghavendra swamy",
    "guru raghavendra": "raghavendra swamy",

    "subramanya": "murugan",
    "subramani": "murugan",
    "skanda": "murugan",

    "vratham": "pooja",
    "vratam": "pooja",
     
     # Suprabhata variants
    "suprabhatam": "suprabhata",
    "suprabatham": "suprabhata",
    "suprabhatham": "suprabhata",

    # ✅ ANDAL / GODA
    "goda": "andal",
    "goda devi": "andal",
    "godadevi": "andal",
    "kodai": "andal",
    "andal": "andal",
    "godha": "goda",

    # ✅ TULASI
    "tulasi": "tulasi",
    "tulsi": "tulasi",
    "tulasi devi": "tulasi",
    "tulsi devi": "tulasi",
    "vrinda devi": "tulasi",

    # ✅ MEENAKSHI
    "meenakshi": "meenakshi",
    "meenkashi": "meenakshi",
    "meenakshi ammavaru": "meenakshi",
    "madurai meenakshi": "meenakshi",

    # Satyanarayana – full phrases only
    "satyanarayanaa": "satyanarayana",
    "satyanarayaana": "satyanarayana",
    "satya narayana": "satyanarayana",
    "satya narayan": "satyanarayana",
    
    # Pooja variants
    "vratham": "pooja",
    "vratam": "pooja",
}


    


__all__ = [
    "WEEKLY_EVENTS",
    "DISPLAY_WEEKLY_NAMES",
    "CANONICAL_WEEKLY_KEYS",
    "MONTH_NORMALIZATION_MAP",
    "CANONICAL_INTENTS",
    "DAILY_SCHEDULE",
    "GLOBAL_NORMALIZATION_MAP",
    "RITUAL_NORMALIZATION",
    
]

HOMAMS_DATA = {
    "list": [
        "Sudarshana Homam",
        "Lakshmi Homam",
        "Venkateswara Homam",
        "Ganapathi Homam",
        "One Graha Homam",
        "Udhaka Shanthi Homam",
        "Ayush Homam",
        "Chandi Homam",
        "Durga Homam",
        "Rudra Homam",
        "Mrutyunjaya Homam",
        "Lakshmi Hayagriva Homam",
        "Lakshmi Narasimha Homam",
        "Dhanvantari Homam",
        "Saraswati Homam",
        "Nava Graha Homam"
    ],
   
}

HOMAM_SPONSORSHIP_KEYS = {
    "ayush homam": "ayush_homam",
    "chandi homam": "chandi_homam",
    "sudarshana homam": "homam_individual_sudarsana_lakshmi_venkateswa_indiv",
    "navagraha homam": "navagraha_homam",
}


# ============================================================
# LUNAR FESTIVAL MAP (USED BY PANCHANG / FESTIVAL LOGIC)
# ============================================================

LUNAR_FESTIVAL_MAP = {
    "karthika poornima": {
        "month": "november",
        "keywords": ["karthika", "kartika"]
    },
    "guru poornima": {
        "month": "july",
        "keywords": ["guru"]
    },
    "sharad poornima": {
        "month": "october",
        "keywords": ["sharad"]
    }
}

def temple_manager_contact() -> str:
    return (
        "📞 TEMPLE MANAGER CONTACT\n"
        "• Phone: 303-898-5514\n"
        "• Email: manager@svtempleco.org"
    )

# ============================================================
# ARJITHA / PRIVATE POOJA KEYWORDS (INTENT ROUTING)
# ============================================================

ARJITHA_PRIMARY_KEYWORDS = [
    "arjitha", "arjita",
]

ARJITHA_SERVICE_KEYWORDS = [
    "private pooja", "private puja",
    "home pooja", "home puja",
    "pooja at home", "puja at home",
    "services offered", "service offered",
    "pooja services", "puja services",
    "seva list", "arjitha list", "arjitha seva list",
    "pooja fee", "puja fee",
    "at home", "at temple",
    "fees", "fee",
    "sponsorship", "amount", "cost", "price", 
    "priests for private pooja", "priests for private pooja services",
    "priests for pooja services", "priests for puja services",
    "need priests", "need priests for home puja"
    "arrange priests"
]

ARJITHA_CEREMONY_KEYWORDS = [
    "gruhapravesam", "vaastu", "vaastu puja",
    "upanayanam",
    "wedding", "nischitartham", "snathakam",
    "seemantham",
    "namakaranam",
    "anna prasana", "annaprasana",
    "aksharabhyasam", "akshraabhyasam",
    "last rites", "srardham", "shradham",
    "pinda pradanam", "tila tarpanam",
    "shanku sthaapana", "bhoomi pooja",
    "shashti poorthi",
    "kalyanotsavam",
    "vastra samarpanam",
    "swarna pushpaarchana",
    "hair offering",
]

# ✅ Final combined list (use everywhere)
ARJITHA_TRIGGER_KEYWORDS = sorted(set(
    ARJITHA_PRIMARY_KEYWORDS
    + ARJITHA_SERVICE_KEYWORDS
    + ARJITHA_CEREMONY_KEYWORDS
))

ARJITHA_FEES = {
    "Abhishekam – Individual (Shiva/Ganapati/Hanuman/Sai Baba)": {"temple": 151, "home": 251},
    "Abhishekam – Individual (Kalyana Srinivasa / Sri Devi / Bhu Devi)": {"temple": 151, "home": 251},
    "Abhishekam – Mahalakshmi or Sri Andal (Moola Murthy) – Regular scheduled": {"temple": 116, "home": None},
    "Abhishekam – Saamoohika (Shiva/Ganapati/Hanuman/Sai Baba) – Regular scheduled": {"temple": 51, "home": None},
    "Abhishekam – Venkateswara (Moola Murthy) – Regular scheduled": {"temple": 151, "home": None},
    "Aksharaabhyasam": {"temple": 101, "home": 201},
    "Andal Kalyanam – Individual": {"temple": 251, "home": 351},
    "Anna Prasana": {"temple": 101, "home": 201},
    "Archana": {"temple": 21, "home": None},
    "Ayush Homam": {"temple": 151, "home": 201},
    "Chandi Homam": {"temple": 401, "home": 501},
    "First Year Birthday (Astotharam & Ashirvachanam)": {"temple": 51, "home": None},
    "Graha Puja (One)": {"temple": 31, "home": None},
    "Gruhapravesam with Vaastu Puja": {"temple": None, "home": 251},
    "Gruhapravesam with Vaastu Puja, Homam & Satyanarayana Vratham": {"temple": None, "home": 401},
    "Gruhapravesam with Vaastu Puja & (Homam OR Satyanarayana Vratham)": {"temple": None, "home": 351},
    "Hair-Offering": {"temple": 101, "home": 151},
    "Hanuman Vada Mala (108 Vada – minimum 7 days notice)": {"temple": 151, "home": None},
    "Hiranya Srardham (Pinda Shradham)": {"temple": 101, "home": 151},
    "Homam – Individual (Sudarsana/Lakshmi/Venkateswara/Ganapathi/One Graha/Udhaka Shanthi)": {"temple": 151, "home": 251},
    "Kalyanotsavam – Individual": {"temple": 251, "home": 501},
    "Kalyanotsavam – Saamoohika": {"temple": 151, "home": None},
    "Last Rites – 1 day": {"temple": 201, "home": None},
    "Last Rites – 3 day event": {"temple": 501, "home": None},
    "Last Rites – 5 day event": {"temple": 751, "home": None},
    "Last Rites – 7 day event": {"temple": 1116, "home": None},
    "Naamakaranam (If Punyahavachanam already done)": {"temple": 116, "home": 201},
    "Naamakaranam and Punyahavachanam": {"temple": 251, "home": None},
    "Navagraha Puja": {"temple": 116, "home": None},
    "Nischitartham": {"temple": 251, "home": 351},
    "Pinda Pradanam with Homam": {"temple": 151, "home": 201},
    "Punyahavachanam (New born – performed at home only)": {"temple": None, "home": 201},
    "Rudrabhishekam": {"temple": 151, "home": 251},
    "Rudrabhishekam (with Homam)": {"temple": 301, "home": 401},
    "Sahasranaama Archana (1008 Names)": {"temple": 116, "home": None},
    "Sani Graha Puja (Thailaabhishekam)": {"temple": 51, "home": None},
    "Satyanarayana Swamy Vratham – Saamoohika": {"temple": 116, "home": None},
    "Satyanarayana Swamy Vratham – Individual": {"temple": 151, "home": 201},
    "Seemantham": {"temple": 151, "home": 201},
    "Seemantham (with Homam)": {"temple": 201, "home": 351},
    "Shanku Sthaapana (Bhoomi Pooja)": {"temple": 201, "home": None},
    "Shashti Poorthi (60th Birthday)": {"temple": 351, "home": 451},
    "Sudarsana Homam – Saamoohika (Regular scheduled)": {"temple": 116, "home": None},
    "Swarna Pushpaarchana – Individual": {"temple": 101, "home": None},
    "Swarna Pushpaarchana – Saamoohika": {"temple": 51, "home": None},
    "Tila Tarpanam": {"temple": 51, "home": 101},
    "Upanayanam": {"temple": 351, "home": 451},
    "Upanayanam (Prev day – Nandhi etc.)": {"temple": 151, "home": 251},
    "Vahana/Car Pooja (Archana included)": {"temple": 51, "home": 201},
    "Varalakshmi Vratham – Individual": {"temple": 151, "home": 201},
    "Wedding": {"temple": 501, "home": 601},
    "Wedding Snathakam (Prev day)": {"temple": 151, "home": 251},
    "Vastra Samarpanam – Venkateswara Swamy (Temple Provides)": {"temple": 1116, "home": None},
    "Vastra Samarpanam – Venkateswara Swamy (Devotee Provides)": {"temple": 516, "home": None},
    "Vastra Samarpanam – Andal (1 Saree 6 yds) Temple Provides": {"temple": 301, "home": None},
    "Vastra Samarpanam – Andal (1 Saree 6 yds) Devotee Provides": {"temple": 151, "home": None},
    "Vastra Samarpanam – Maha Lakshmi (2 Sarees 6 yds) Temple Provides": {"temple": 401, "home": None},
    "Vastra Samarpanam – Maha Lakshmi (2 Sarees 6 yds) Devotee Provides": {"temple": 151, "home": None},
    "Vastra Samarpanam – Kalyanam (Temple provides: 1 silk dhothi + 2 silk sarees)": {"temple": 516, "home": None},
    "Vastra Samarpanam – Kalyanam (Devotee provides: 1 silk dhothi + 2 silk sarees)": {"temple": 201, "home": None},
    "Venkateswara Nitya Archana – Monthly": {"temple": 116, "home": None},
    "Venkateswara Nitya Archana – Annual": {"temple": 1116, "home": None},
    "Venkateswara Saturday Archana – Monthly": {"temple": 51, "home": None},
    "Venkateswara Weekend Archana – Annual": {"temple": 516, "home": None},
}

