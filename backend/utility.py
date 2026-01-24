##backend/utility.py
from backend.constants import CANONICAL_INTENTS, GLOBAL_NORMALIZATION_MAP, MONTH_NORMALIZATION_MAP,WEEKLY_EVENTS


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

import re
from difflib import get_close_matches
from backend.items_catalog_query import ITEMS_REQUIRED

INTENT_NORMALIZATION = {

    # ---- TIME ALIASES ----
    "tomo": "tomorrow",
    "tmr": "tomorrow",
    "tmrw": "tomorrow",
    "tomorow": "tomorrow",
    "tomo's" : "tomorrow",
    "tomorrow's": "tomorrow",

    "todays": "today",
    "today's": "today",

    # ---- COMMON TYPOS ----
    "scheduel": "schedule",
    "shedule": "schedule",
    "hapening": "happening",
    "happning": "happening",
}




def _sanitize(text: str) -> str:
    """Clean up text and remove thinking tags"""
    if not isinstance(text, str):
        text = str(text)

    # Remove thinking/reasoning tags
    patterns = [
        r"(?is)<think>.*?</think>",
        r"(?is)```(?:thinking|reasoning|thoughts).*?```",
    ]
    for pat in patterns:
        text = re.sub(pat, "", text, flags=re.DOTALL | re.IGNORECASE)

    return text.strip()


# ============================================================
# FORMAT RAG RESULTS
# ============================================================

def _format_bullets(raw: str) -> str:
    """Simple bullet point formatting"""
    if not raw or not raw.strip():
        return ""
    
    lines = [l.strip() for l in raw.split("\n") if l.strip()]
    formatted = []
    
    for line in lines:
        # Skip if already has bullet
        if line.startswith(("•", "-", "*")):
            formatted.append(line)
        else:
            formatted.append(f"• {line}")
    
    return "\n".join(formatted)

# ============================================================
# MAIN ANSWER FUNCTION
# ============================================================
# --- SESSION TRACKING ---
# Global set to track users seen during the current Lambda execution context.
# This ensures "Om Namo Venkatesaya" only appears on the first interaction.



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
          "sahasranamam",
          "sahasranama",
          "sahasranamams",
          "parayanam",
          "recitation",
          "chanting",
    ]
)

def normalize_intent(q: str) -> str:
    q = q.lower().strip()

    # ✅ remove punctuation BUT keep apostrophe (so "what's" stays)
    q = re.sub(r"[^\w\s']+", " ", q)
    q = re.sub(r"\s+", " ", q).strip()

    # 1️⃣ Token-level normalization
    words = q.split()
    words = [INTENT_NORMALIZATION.get(w, w) for w in words]
    q = " ".join(words)

    # 2️⃣ Phrase-level canonical intent normalization
    for canonical, variants in CANONICAL_INTENTS.items():
        for v in variants:
            if v in q:
                q = q.replace(v, canonical)

    return q



def norm(q: str) -> str:
    return q.lower().strip()

def normalize_query(q: str) -> str:
    q = q.lower().strip()
    q = q.replace("’", "'")  # normalize apostrophe

    print("in normalize query", q)

    # Add space after punctuation like sat.hours -> sat. hours
    q = re.sub(r"([.,!?/])", r"\1 ", q)

    for k in sorted(GLOBAL_NORMALIZATION_MAP, key=len, reverse=True):
        v = GLOBAL_NORMALIZATION_MAP[k]

        # Strip accidental spaces inside your map keys/values
        k_clean = k.strip()
        v_clean = v.strip()

        # ✅ Safe boundary: works for "sat.", "tue.", "jan.", etc.
        pattern = rf"(?<!\w){re.escape(k_clean)}(?!\w)"

        new_q = re.sub(pattern, v_clean, q)
        if new_q != q:
            q = new_q
            print(f"mapped '{k_clean}' → '{v_clean}' => {q}")

    # cleanup extra spaces
    q = re.sub(r"\s+", " ", q).strip()
    return q




def autocorrect_query(q: str, cutoff: float = 0.88) -> str:
    """
    Lightweight spelling correction using stdlib only.
    Corrects ONLY close matches from known temple vocabulary.
    """
    words = q.split()
    corrected = []

    for w in words:
        if len(w) < 4 or not w.isalpha():
            corrected.append(w)
            continue

        matches = get_close_matches(
            w,
            TEMPLE_VOCAB,
            n=1,
            cutoff=cutoff
        )

        corrected.append(matches[0] if matches else w)

    return " ".join(corrected)

MANAGER_APPEND_SET = [
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
def finalize(out: str, q: str) -> str:
    out = _sanitize(out)
    out = _format_bullets(out)

    q_norm = normalize_query(q)
    print("i am in finalize")

    # Append (do NOT replace) temple manager contact
    if q_norm in MANAGER_APPEND_SET:
        if "CONTACT THE TEMPLE MANAGER" not in out.upper():
            out += (
                "\n\n• For further details, please contact the Temple Manager."
            )
        print("after append", out)

    return out

