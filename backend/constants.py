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
    " jan ": " january ",
    " jan.": " january",
    " january ": " january ",

    " feb ": " february ",
    " feb.": " february",
    " february ": " february ",

    " mar ": " march ",
    " mar.": " march",
    " march ": " march ",

    " apr ": " april ",
    " apr.": " april",
    " april ": " april ",

    " jun ": " june ",
    " jun.": " june",
    " june ": " june ",

    " jul ": " july ",
    " jul.": " july",
    " july ": " july ",

    " aug ": " august ",
    " aug.": " august",
    " august ": " august ",

    " sep ": " september ",
    " sept ": " september ",
    " sep.": " september",
    " september ": " september ",

    " oct ": " october ",
    " oct.": " october",
    " october ": " october ",

    " nov ": " november ",
    " nov.": " november",
    " november ": " november ",

    " dec ": " december ",
    " dec.": " december",
    " december ": " december ",
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
    "10:00 AM – Sri Venkateswara Nitya Archana"
]

GLOBAL_NORMALIZATION_MAP = {
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
    "ayush": "ayush homam",
    "chandi": "chandi homam",
    "sudarshana": "sudarshana homam",
    "sudarshan": "sudarshana homam",
    "navagraha": "nava graha homam",
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


