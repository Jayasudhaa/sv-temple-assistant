# backend/ask_temple.py

import os, json, re, boto3
from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo
from .retrieval import get_chunks
import logging
from typing import Optional, List
from enum import Enum
from difflib import get_close_matches

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
_bedrock_runtime = None
BEDROCK_MODEL_ID = os.getenv(
    "BEDROCK_MODEL_ID",
    "us.anthropic.claude-3-5-haiku-20241022-v1:0"
)
FULL_DAY_OPEN_HOLIDAYS = {
    "christmas",
    "thanksgiving",
    "new year",
    "new years",
    "memorial day",
    "labor day",
    "martin luther king day"
}



def get_bedrock_client():
    global _bedrock_runtime
    if _bedrock_runtime is None:
        try:
            _bedrock_runtime = boto3.client(
                service_name="bedrock-runtime",
                region_name=os.getenv("AWS_REGION", "us-east-1")
            )
        except Exception as e:
            logger.error("Failed to initialize Bedrock client", exc_info=True)
            _bedrock_runtime = None
    return _bedrock_runtime

from datetime import date
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MAASA_FILE = BASE_DIR/"data_raw"/"Panchang"/"2026"/"Maasa_Paksham.txt"

import re

def get_maasa_paksham(target_date: date) -> tuple[str, str] | None:
    logger.info("Resolved MAASA_FILE = %s", MAASA_FILE.resolve())
    logger.info("Files in Panchang/2026: %s",
            list((BASE_DIR / "data_raw" / "Panchang" / "2026").iterdir()))

    if not MAASA_FILE.exists():
        logger.error("❌ Maasa_Paksham.txt NOT FOUND")
        return None

    month = target_date.strftime("%b")   # Jan, Feb, ...
    day = target_date.day

    current_maasa: str | None = None

    with MAASA_FILE.open(encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()

            # ─────────────────────────────────────────
            # 1️⃣ Detect MAASA header
            # Example: MONTH 1: PUSHYA MAASA (January 1-18)
            # ─────────────────────────────────────────
            m = re.match(r"MONTH\s+\d+:\s+([A-Z\s]+)\s+MAASA", line)
            if m:
                current_maasa = f"{m.group(1).title()} Maasa"
                logger.info("Detected Maasa header: %s", current_maasa)
                continue

            # Skip until a Maasa is known and row contains '|'
            if not current_maasa or "|" not in line:
                continue

            # ─────────────────────────────────────────
            # 2️⃣ Parse date range + paksham
            # Example rows:
            # Jan 1-18 | Sukla Paksham | ...
            # Jan 19-Feb 1 | Krishna Paksham | ...
            # ─────────────────────────────────────────
            parts = [p.strip() for p in line.split("|")]
            if len(parts) < 2:
                continue

            date_range, paksham = parts[0], parts[1]

            if "-" not in date_range or "Paksham" not in paksham:
                continue

            try:
                start, end = date_range.split("-")

                # Start date
                sm, sd = start.split()
                sd = int(sd)

                # End date (handle both formats)
                end_parts = end.split()
                if len(end_parts) == 1:
                    # Jan 1-18
                    em = sm
                    ed = int(end_parts[0])
                else:
                    # Jan 19-Feb 1
                    em, ed = end_parts
                    ed = int(ed)

            except Exception as e:
                logger.warning("Skipping malformed line: %s | error=%s", line, e)
                continue

            # ─────────────────────────────────────────
            # 3️⃣ Match date
            # ─────────────────────────────────────────
            if sm == em:
                if sm == month and sd <= day <= ed:
                    return current_maasa, paksham
            else:
                if (month == sm and day >= sd) or (month == em and day <= ed):
                    return current_maasa, paksham

    logger.warning("⚠️ No Maasa/Paksham match for %s", target_date)
    return None



# ============================================================
# ITEMS REQUIRED FOR POOJAS (Complete Temple Website Data)
# ============================================================

POOJA_SAMAGRI_URL = "https://svtempleco.org/Home/PoojaSamagri.html"

ITEMS_REQUIRED = {
    "general": {
        "name": "General Pooja Items",
        "items": """• Fresh flowers (jasmine, roses, or marigold)
• Fruits (banana, apple, orange - seasonal fruits)
• Coconut (1 whole)
• Betel leaves and betel nuts
• Turmeric and kumkum
• Incense sticks
• Camphor
• Ghee or oil for lamp""",
        "note": "Temple can provide most items for standard poojas"
    },

    "satyanarayana": {
        "name": "Satyanarayana Swamy Pooja at Temple",
        "items": """• Flowers - 3 Bunches
• Fruits - 3 varieties
• Betel leaves - 20 Nos.
• Coconuts - 8 Nos.
• Blouse piece - 1 No.
• Towel - 1 No.
• Milk (Organic) - 1 Gallon
• Ghee - 1 Lb
• Cashews - 1 Packet
• Sugar - 2 Lbs.
• Yogurt - 1 Box
• Honey - 1 Small bottle
• Turmeric and Kumkum - 1 Packet each
• Chandanam/Sandalwood powder - 1 Packet
• Camphor - 1 Packet
• Rice - 2 Lbs.
• Agarbatti/Incense sticks - 1 Packet
• Navadhanyam - 1 Packet
• Betel Nuts - 20 Nos.
• Dry Dates - 20 Nos.
• Quarter coins - 20 Nos.
• Mango leaves garland - 1 No.
• Rava Prasadam (Kesari)""",
        "note": "Full Moon Day at 6:30 PM"
    },

    "gruhapravesam": {
        "name": "Gruhapravesam (Housewarming) and Vastu Pooja",
        "items": """• Turmeric, Chandanam and Kumkuma - 1 Packet each
• Navadhanyalu - 1 Packet
• Milk - 0.5 gallon
• Curd - 1 Packet
• Honey - 1 small bottle
• Sugar - 0.5 lb
• Agarbatti, Karpuram/Camphor - 1 Packet each
• White Pumpkin Whole - 1 No.
• Rice - 2 Lbs
• Blouse piece - 1 No.
• Towel - 1 No.
• Navadhanyam - 1 Packet
• Quarter Coins - 40 Coins
• Rava Prasadam (Kesari)
• Betel Leaves - 20 Nos.
• Betel Nuts - 20 Nos.
• Fruits - 12 Bananas, 5 different varieties
• Flowers - 2 Bunches
• Coconut - 6 No.
• Dry Dates - 25 Nos.
• Lemons - 4 Nos.
• Hammer - 1 No.
• New Vessel for boiling milk - 1 No.
• Aluminum Trays - 4 Nos.
• Picture or Idol of a cow - 1 No.
• God Pictures - Your choice
• Lamps - 2 Nos. with wicks
• Matchbox or lighter - 1 No.
• Oil or Ghee for lamp
• Knife - 1 No.
• Scissors - 1 No.
• Mango leaves garland - 1 No.
• Flower garland - 1 No.
• Kalasam - 1 No.""",
        "note": "Contact temple in advance for home pooja arrangements"
    },

    "vastu": {
        "name": "Vastu Pooja",
        "items": """[Same as Gruhapravesam - see above]
Contact temple for specific Vastu Shanti requirements""",
        "note": "For Vastu Shanti. Contact for priest arrangement"
    },

    "homam": {
        "name": "Homam (Fire Ceremony)",
        "items": """• Dry coconuts - 6 Nos.
• Ghee - 1 Lb
• Cashews - 1 Packet
• Elaichi (Cardamom) - 1 Packet
• Silk blouse piece - 1 No.
• Big Aluminium trays - 5 Nos.
• Paper bowls - 5 Nos.
• Navadhanyam - 1 Packet
• Mango leaves garland - 1 No.""",
        "note": "Contact temple for specific homam requirements"
    },

    "archana": {
        "name": "Archana Items",
        "items": """• Fresh flowers (108 for 108 names)
• Fruits
• Coconut
• Betel leaves""",
        "note": "For special archana services"
    },

    "kalyanam": {
        "name": "Venkateswara Kalyanam (Divine Wedding)",
        "items": """• Milk (Organic) - 1/2 Gallon
• Coconuts - 3 Nos.
• Flower garlands - 3 Nos. (2.5 Feet long - 2 Nos., 3 Feet - 1 No.)
• Pattu (silk) sarees - 2 Nos. (applicable pattu saree to Venkateswara Swamy)
• Dry coconuts - 2 Nos.
• Betel leaves - 20 Nos.
• Betel Nuts - 20 Nos.
• Jeelakara Bellam (Cumin seeds and Jaggery) - 1 small packet each
• Agarbatti/Incense sticks, Karpuram/Camphor - 1 Packet each
• Turmeric, Chandanam and Kumkum - 1 Packet each
• Rice - 2 Kgs.
• Flowers - 2 bunches
• Fruits - 5 different
• Blouse Piece - 2 No.
• Honey - 1 small bottle
• Talambralu (Raw turmeric rice) - 1.5 Kgs

IN ADDITION (if done at home):
• Curd - 1 No
• Steel plates - 4 No.
• Kalasam - 2 No.
• Panchapatra - 2 No.
• Udharani (spoons) - 2 No.
• Mango Leaves - One bunch""",
        "note": "2nd Week Saturday 11:00 AM"
    },

    "bhoomi_pooja": {
        "name": "Bhoomi Pooja (Foundation Ceremony)",
        "items": """• Turmeric, Chandanam and Kumkuma - 1 Packet each
• Agarbatti, Karpuram/Camphor, Match Box - 1 Packet each
• Rice - 1.5 Kgs
• Towels - 2 Nos.
• Blouse piece - 1 No.
• Navadhanyam - 2 Packet
• Navarathnalu - 1 Packet (Optional)
• Quarter coins - 25 Nos.
• Betel leaves - 15 Nos.
• Betel Nuts - 15 Nos.
• Coconuts - 4 Nos.
• Flowers - 2 Bunches
• Fruits - 3 Varieties
• Bricks (any color) - 9 Nos.
• Mango Leaves - One bunch""",
        "note": "For new construction foundation ceremony"
    },

    "annaprasana": {
        "name": "Anna Prasana (First Rice Ceremony)",
        "items": """• Turmeric, Chandanam and Sindhuram - 1 Packet each
• Agarbatti, Karpuram/Camphor, Match Box - 1 Packet each
• Rice - 1 Lb
• Blouse piece - 1 No.
• Betel leaves - 10 Nos.
• Betel Nuts - 10 Nos.
• Coconuts - 2 Nos.
• Flowers - 1 Bunch
• Fruits - 12 Bananas, 1 Orange bag
• Ghee or Sesame Oil - 1 Small bottle
• Sweet payasam - Just for feeding baby
• Mango Leaves - One bunch""",
        "note": "Baby's first solid food ceremony"
    },

    "namakaranam": {
        "name": "Namakaranam (Naming Ceremony)",
        "items": """• Turmeric, Chandanam and Sindhuram - 1 Packet each
• Agarbatti, Karpuram/Camphor, Match Box - 1 Packet each
• Rice - 1 Lb
• Betel leaves - 10 Nos.
• Betel Nuts - 10 Nos.
• Coconuts - 2 Nos.
• Flowers - 1 Bunch
• Fruits - 12 Bananas, 1 Orange bag
• Honey - 1 Small bottle
• Quarter Coins - 20 Nos.
• Milk (Organic) - 1 Gallon
• Dry Dates - 10 Nos.
• Mango Leaves - One bunch""",
        "note": "Baby naming ceremony"
    },

    "hair_offering": {
        "name": "Hair Offering (Mundan)",
        "items": """• Turmeric, Chandanam and Kumkuma - 1 Packet each
• Agarbatti, Karpuram/Camphor, Match Box - 1 Packet each
• Rice - 1 Lb
• Yellow Cloth - 1 Yard
• Betel leaves - 10 Nos.
• Betel Nuts - 10 Nos.
• Scissors - 1 No.
• Flowers - 1 Bunch
• Fruits - 12 Bananas, 1 Orange bag
• Quarter Coins - 10 Nos.
• Milk (Organic) - 1 Gallon""",
        "note": "Child's first hair offering ceremony"
    },

    "seemantham": {
        "name": "Seemantham (Baby Shower)",
        "items": """• Turmeric, Chandanam and Kumkuma - 1 Packet each
• Agarbatti, Karpuram/Camphor, Match Box - 1 Packet each
• Rice - 2 Lbs
• Coconuts - 2 Nos.
• Small Mirror and Comb - 1 No. each
• Flowers - 1 Bunch
• Fruits - 12 Bananas, 1 Orange bag
• Sumangali Sets (Turmeric & Kumkum, Blouse piece, Comb, Bangles) - 7 Sets
• Milk (Organic) - 1 Gallon
• Mango leaves - One bunch""",
        "note": "Traditional baby shower ceremony for pregnant women"
    },

    "nischitartham": {
        "name": "Nischitartham (Engagement Ceremony)",
        "items": """• Turmeric and Kumkum - 2 Cups each
• Agarbatti, Karpuram/Camphor - 2 Packets each
• Rice - 3 Lbs
• Blouse piece - 2 Nos.
• Betel leaves and Nuts - 20 Nos.
• Coconuts - 4 Nos.
• Flower Garlands - 2 Nos. Grand malas, 2+2 for both parents
• Loose Flower - 1 bunch
• Fruits - 5 varieties, 5 plates full
• Quarter Coins - 11 Nos.
• Chandanam - 1 Packet
• Lakshmi photo and any other photos - 1 + 1 Nos.
• Mango Leaves (if available) - 1 Bunch
• Kitchen Paper Towel - 1 Roll
• Oil Lamps - 2 Nos.
• Wooden planks to sit for pooja - 3 Nos.
• Any Sweet Prasadam - 1 Bowl
• Steel Glass with Spoons - 2 Nos.
• Kalasam Chembu - 1 No.
• Different varieties of Phalagarams (Muruku, Paruputhenga, Sweets etc.) - 4 Plates full
• New dress for the Groom and his parents
• New dress for the Bride and her parents
• Coconuts powder mixed with sugar candy and sugar powder""",
        "note": "Hindu engagement ceremony. Contact temple for priest arrangement"
    },

    "hindu_wedding": {
        "name": "Hindu Wedding Ceremony",
        "items": """• Turmeric and Kumkum - 1 Packet each
• Betel Leaves and Nuts - 20 Nos. each
• Dry Turmeric Root - 1 Packet
• Dry Dates - 1 Packet
• Agarbatti/Incense sticks, Karpuram/Camphor - 1 Packet each
• Rice - 20 Lbs
• Cloth Towels - 2 Nos.
• Sandal Powder - 1 Packet
• Jeera - 1 Packet
• Jaggery - 1 Packet
• Ghee - 250 Grams
• Dry Coconut Halves - 4 Nos.
• Coconuts - 4 Nos.
• Blouse Pieces - 2 Nos.
• Mangalyam/Mangalasutra - 1 Set
• Quarter Coins - 28 Nos. (and 40 for Telugu weddings)
• Cotton Thread - 1 No.
• Steel/Glass Tumblers - 4 Nos.
• Ring for the Groom - Optional
• Big Steel Plate for Pada Pooja (Tray size) - 1 No.
• Flower Garlands - 2 Nos.
• Silk clothes for Bride and Groom
• Flowers - 3 bunches
• Brass/Silver/Gold plate for washing Bride
• Kalasam - 3 No.
• Plates - 4 No.
• Paper bowls - 10 No.
• Deepam Kundulu (Lamp/Vellekku) - 2 Nos.
• Vathulu - 1 No.
• Sesame oil - 1 No.
• White clothes - 2 No (each 3 or 4 yards)
• Steel Binde - 1 (for Telugu weddings)""",
        "note": "Complete Hindu wedding ceremony. Contact temple well in advance"
    },

    "hiranya_sharddham": {
        "name": "Hiranya Sharddham",
        "items": """• Flowers and Fruits
• Betel Leaves and Nuts - 10 Nos. each
• Rice - 1 Bag
• Black Sesame Seeds - 1 Small Packet
• Moong Dal - 1 Small Packet
• Urad Dal - 1 Small Packet
• Oil - 1 Small Bottle
• Jeera - 1 Small Packet
• Red Chilly - 1 Small Packet
• Tamarind - 1 Small Packet
• Jaggery - 1 Small Packet
• Ghee - 1 Bottle
• Vegetables - Mixed
• Milk (Organic) - 1 Gallon
• Quarter Coins - 10 Nos.""",
        "note": "Memorial ritual for departed souls. Contact temple for scheduling"
    },

    "nava_graha": {
        "name": "Nava Graha Pooja (Nine Planets)",
        "items": """• Sani Graha: Black sesame seeds 50 grams, Sesame oil, Fruits & Flowers
• Rahuvu Graha: Whole Urad 50 grams (Minumalu), Sesame oil, Fruits & Flowers
• Ketuvu Graha: Horse gram 50 grams (Ulavalu), Sesame oil, Fruits & Flowers
• Surya Graha: Wheat 50 grams, Sesame oil, Fruits & Flowers
• Chandra Graha: Rice 50 grams, Sesame oil, Fruits & Flowers
• Angaraka Graha: Whole lentil 50 grams (Kandulu), Fruits & Flowers
• Budha Graha: Whole Moong 50 grams (Pesalu), Fruits & Flowers
• Guru Graha: Senagalu 50 grams, Sesame oil, Fruits & Flowers
• Sukra Graha: White Black eye peas 50 grams (white Bobbarlu), Sesame oil, Fruits & Flowers""",
        "note": "Planetary worship for removing obstacles and planetary doshas"
    },

    "aksharabhyasam": {
        "name": "Aksharabhyasam (Vidyarambham)",
        "items": """• Fruits - 12 Bananas, 1 Bag of Oranges
• Betel Leaves and Nuts - 10 Nos. each
• Rice - 1 Lb
• Flowers - 1 Bunch
• Turmeric, Kumkum and Chandanam - 1 Packet each
• Agarbatti and Camphor - 1 Packet each
• Dry Dates - 10 Nos.
• Coconut - 2 Nos.
• Slate - 1 No.
• Chalk - 1 No.
• Notebook - 2 Nos.
• Pen - 1 No.
• Ghee or Oil - 1 Bottle
• Milk (Organic) - 1 Gallon
• Quarter Coins - 20 Nos.
• Mango Leaves - One bunch""",
        "note": "Child's educational initiation ceremony (first writing)"
    },

    "abhishekam": {
        "name": "Abhishekam Items",
        "items": """• Fruits - 12 Bananas, 1 Bag of Oranges
• Sugar - 1 Small Packet
• Rice - 1 Lb
• Flowers - 1 Bunch
• Turmeric, Kumkum and Chandanam - 1 Packet each
• Agarbatti and Camphor - 1 Packet each
• Honey - 1 Bottle
• Coconut - 3 Nos.
• Coconut Water - 1 Big Bottle
• Any Variety of Juice - 1 Gal
• Ghee - 1 Bottle
• Milk (Organic) - 1 Gallon
• Organic Yogurt - 1/4 Gallon""",
        "note": "Check weekly abhishekam schedule. Complete ritual bathing of deity"
    },

    "half_saree": {
        "name": "Half Saree Function (Ritu Kala Samskara)",
        "items": """• Turmeric, Kumkum and Chandanam - 1 Packet each
• Agarbatti and Camphor - 1 Packet each
• Fruits - 3 Varieties
• Flowers - Your choice
• Rice - 2 Lbs
• Coconut - 2 Nos.
• Blouse Piece - 2 Nos.
• Betel Leaves - 8 Nos.
• Betel Nuts - 1 Packet
• Quarter Coins - 25 Nos.
• Dry Fruits - 1 Packet
• Mango Leaves - One bunch
• Half saree - 1 No.
• Kalasam - 1 No.""",
        "note": "Traditional coming-of-age ceremony for young girls"
    },

    "any_homam": {
        "name": "Any Homam (General Requirements)",
        "items": """• Turmeric and Kumkum - 1 Small Packet each
• Betel Leaves and Nuts - 10 Nos. each
• Flowers - 2 Bunches
• Agarbatti/Incense sticks, Karpuram/Camphor - 1 Small Packet each
• Rice - 1 Lb
• Coconuts - 3 Nos.
• Dry Coconuts - 6 Packets
• Navadhanyam - 1 Small Packet
• Blouse Piece - 1 No.
• Kalasam - 1 No. (Skip if pooja is at temple)
• Cups and Plates (Skip if pooja is at temple)
• Ghee - 1 Bottle
• Fruits - 2 Varieties
• Sweet Prasadham (Skip if pooja is at temple)
• Mango Sticks - 3 Packets
• Silk Blouse Piece - 1 No.
• Quarter Coins - 20 Nos.
• Mango Leaves - One bunch""",
        "note": "General items for any homam. Contact temple for specific homam requirements"
    },

    "sudarshana": {
        "name": "Sudarshana Homam",
        "items": """• Dry coconuts - 6 Nos.
• Ghee - 1 Lb
• Cashews - 1 Packet
• Elaichi - 1 Packet
• Navadhanyam - 1 Packet
• Mango leaves garland
• Aluminium trays - 5 Nos.
• Paper bowls - 5 Nos.
• Sacred wood
• Sesame seeds""",
        "note": "4th Week Sunday 11:00 AM"
    }
}

# ============================================================
# INTENTS
# ============================================================

class Intent(str, Enum):

    STORY = "STORY"
    FOOD = "FOOD"
    TEMPLE_HOURS = "TEMPLE_HOURS"
    LOCATION = "LOCATION"
    VEDIC_RECITATION = "VEDIC_RECITATION"
    DAILY_POOJA = "DAILY_POOJA"
    WEEKLY_POOJA = "WEEKLY_POOJA"
    MONTHLY_POOJA = "MONTHLY_POOJA"
    YEARLY_POOJA = "YEARLY_POOJA"

    SATYANARAYANA_POOJA = "SATYANARAYANA_POOJA"

    WEEKLY_ABHISHEKAM = "WEEKLY_ABHISHEKAM"

    EVENTS_TODAY = "EVENTS_TODAY"
    EVENTS_WEEKLY = "EVENTS_WEEKLY"
    EVENTS_MONTHLY = "EVENTS_MONTHLY"
    EVENTS_YEARLY = "EVENTS_YEARLY"
    EVENTS_RELATIVE = "EVENTS_RELATIVE"

    PANCHANG_TODAY = "PANCHANG_TODAY"
    PANCHANG_TOMORROW = "PANCHANG_TOMORROW"
    PANCHANG_DATE = "PANCHANG_DATE"
    LUNAR_DATES = "LUNAR_DATES"
    EVENTS_UPCOMING = "EVENTS_UPCOMING"
    HOMAMS = "HOMAMS"
    HOMAM_ITEMS = "HOMAM_ITEMS"

    ARJITHA_SEVA = "ARJITHA_SEVA"
    VAHANA_POOJA = "VAHANA_POOJA"

    CONTACTS = "CONTACTS"
    COMMITTEE = "COMMITTEE"
    CULTURAL = "CULTURAL"

    RAG_FALLBACK = "RAG_FALLBACK"
    ABHISHEKAM_SPONSORSHIP = "ABHISHEKAM_SPONSORSHIP"

ITEM_KEYS = {
    key.replace("_", " "): key
    for key in ITEMS_REQUIRED
}

# ============================================================
# HARD-CODED TEMPLE INFO
# ============================================================

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

# ============================================================
# DAILY & MONTHLY SCHEDULE
# ============================================================

DAILY_SCHEDULE = [
    "09:00 AM – Sri Venkateswara Suprabhata Seva",
    "10:00 AM – Sri Venkateswara Nitya Archana"
]

MONTHLY_SCHEDULE = [
    "Full Moon Day – 06:30 PM – Sri Satyanarayana Swamy Pooja and Vratam"
]
# ============================================================
# GLOBAL QUERY NORMALIZATION
# ============================================================

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

def normalize_query(q: str) -> str:
    q = f" {q.lower().strip()} "

    for src, tgt in GLOBAL_NORMALIZATION_MAP.items():
        q = q.replace(src, tgt)

    for src, tgt in MONTH_NORMALIZATION_MAP.items():
        q = q.replace(src, tgt)

    return q.strip()

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

# ============================================================
# COMMON INSTRUCTIONS
# ============================================================

INSTRUCTIONS = {
    "vahana_pooja": (
        "Walk-ins are welcome subject to availability of priest. "
        "Bring: 4 lemons, 1 coconut, fruits and flowers"
    ),
    "schedule_pooja": (
        "Please contact the temple manager to schedule a pooja."
    ),
}
MANAGER_ESCALATION_KEYWORDS = [
    # Temple administration / leadership
    "priest", "patron member", "patron members",
    "vice treasurer", "vice ec president", "vice secretary",
    "treasurer", "founding member", "founding members", "board of trustees", "vice chairman",

    # Ceremonies & samskaras
    "bheema ratha santhi", "beema ratha santhi","kanakabishekam",
   
    # Vedic rituals
    "avani avittam", "upakarma", "shradha", "shraddha",
    "rudram", "navagraha abisekam",

    # Festivals & utsavams
    "brahmothsavam", "adyayanotsavam",
    "meenakshi kalyanam","pitru paksha","annamacharya day","naraka chaturdashi", "mahalaya", "mahalaya amavasya",

    # Temple programs
    "balavihar", "volunteer", "volunteering",
    "hanuman vada mala", "bhagavad gita class","saraswathy puja","vriksha puja","metla puja","gau mata puja",
     "guru pooja", "swarna pushpa abhishekam",
    "vinayakar chathurthi","ganesh chathurthi","varalakshmi vratham", "vasanth panchami","shanthi pooja",
    "chaath puja","ratha sapthami","ram navami","new year", "ugadi","putthandu", "pradosham",
    "tulsi kalyanam","thai poosam","holi","aadi krithigai","janmashtami","krishna jayanthi",
    
]

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

# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def _is_weekend(now: datetime) -> bool:
    """Check if today is weekend (Saturday=5, Sunday=6)"""
    return now.weekday() in [5, 6]

def _get_year(now: datetime, q: str) -> int:
    """
    Detect year from query or default to current year.
    Supports: '2026', '2027', etc.
    """
    match = re.search(r"\b(20\d{2})\b", q)
    if match:
        return int(match.group(1))
    return now.year


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

# ============================================================
# HOMAMS DATA (FROM ARJITHA SEVA)
# ============================================================

HOMAMS_DATA = {
    "list": [
        "Sudarsana Homam",
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
    "pricing": {
        "individual": {"temple": "$151", "home": "$251"},
        "ayush": {"temple": "$151", "home": "$201"},
        "chandi": {"temple": "$401", "home": "$501"},
        "saamoohika": {"sudarshana": "$116"}
    }
}

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

def homam_list_response() -> str:
    lines = ["🪔 HOMAMS PERFORMED AT THE TEMPLE:\n"]
    for h in HOMAMS_DATA["list"]:
        lines.append(f"• {h}")
    lines.append(temple_manager_contact())
    return "\n".join(lines)


def homam_cost_response(q: str) -> str:
    q = q.lower()
    p = HOMAMS_DATA["pricing"]

    # -------------------------
    # AYUSH HOMAM
    # -------------------------
    if "ayush" in q:
        return (
            "🪔 AYUSH HOMAM – SPONSORSHIP\n\n"
            f"• At Temple: {p['ayush']['temple']}\n"
            f"• At Home: {p['ayush']['home']}\n\n"
            + temple_manager_contact()
        )

    # -------------------------
    # CHANDI HOMAM
    # -------------------------
    if "chandi" in q:
        return (
            "🪔 CHANDI HOMAM – SPONSORSHIP\n\n"
            f"• At Temple: {p['chandi']['temple']}\n"
            f"• At Home: {p['chandi']['home']}\n\n"
            + temple_manager_contact()
        )

    # -------------------------
    # SAAMOOHIKA HOMAM (GROUP)
    # -------------------------
    if "saamoohika" in q or "group" in q:
        return (
            "🪔 SAAMOOHIKA HOMAM (GROUP HOMAM)\n\n"
            f"• Sponsorship per family: {p['saamoohika']['sudarshana']}\n\n"
            + temple_manager_contact()
        )

    # -------------------------
    # DEFAULT – INDIVIDUAL HOMAMS
    # -------------------------
    return (
        "🪔 INDIVIDUAL HOMAM – SPONSORSHIP\n\n"
        f"• At Temple: {p['individual']['temple']}\n"
        f"• At Home: {p['individual']['home']}\n\n"
        + temple_manager_contact()
    )

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

def normalize_intent(q: str) -> str:
    q = q.lower()
    for canonical, variants in CANONICAL_INTENTS.items():
        for v in variants:
            if v in q:
                return q.replace(v, canonical)
    return q

def norm(q: str) -> str:
    return q.lower().strip()

TODAY_WORDS = [
    "today", "todays", "today's"
]

EVENT_WORDS = [
    "event", "events",
    "schedule", "program", "programs", "programme", "programmes",
    "happening", "happenings",
    "special", "function", "functions","festivities",
    "activity", "activities",
    "going on", "on today"
]


def is_events_today(q: str) -> bool:
    q = norm(q)

    has_today = any(w in q for w in TODAY_WORDS)
    has_event = any(w in q for w in EVENT_WORDS)

    return has_today and has_event
def handle_relative_events(q: str, now: datetime) -> str | None:
    # 1️⃣ Resolve target date
    if "tomorrow" in q or "tomo" in q or "tmrw" in q:
        target = now + timedelta(days=1)
        label = "Tomorrow"
    elif "sunday" in q:
        target = now + timedelta(days=(6 - now.weekday()) % 7)
        label = "Sunday"
    elif "saturday" in q or "weekend" in q:
        target = now + timedelta(days=(5 - now.weekday()) % 7)
        label = "Saturday"
    else:
        return None

    ordinal, weekday = get_nth_weekday_of_month(target)
    key = f"{ordinal} {weekday}"

    lines = [
        f"📅 {label} ({target:%B %d, %Y})",
        ""
    ]

    # 2️⃣ Weekly abhishekam / kalyanam
    matched = [
        s for s in WEEKLY_EVENTS.values()
        if s.startswith(key)
    ]

    if matched:
        lines.append("🪔 SPECIAL EVENTS:")
        for m in matched:
            lines.append(f"• {m}")
    else:
        lines.append("• No special abhishekam or kalyanam scheduled.")

    lines.append("")
    lines.append("📿 DAILY POOJA:")
    for d in DAILY_SCHEDULE:
        lines.append(f"• {d}")

    lines.append(temple_manager_contact())
    return "\n".join(lines)

def is_full_day_open_holiday_query(q: str) -> bool:
    q = q.lower()
    return any(h in q for h in FULL_DAY_OPEN_HOLIDAYS)


def classify_intent(q: str) -> Intent:
    q = q.lower()
    # ---------------- VEDIC RECITATIONS (STRICT ESCALATION) ----------------
    if any(w in q for w in [
        "suktham", "sukthams",
        "sahasranamam", "sahasranama", "sahasranamams",
        "nama sankeerthanam", "namasankeerthanam",
        "vishnu sahasranamam", "lalitha sahasranamam",
        "recitation", "chanting", "parayanam"
    ]):
        return Intent.VEDIC_RECITATION
    

    # ---------------- FEDERAL HOLIDAYS → HOURS ----------------
    if is_full_day_open_holiday_query(q):
        return Intent.TEMPLE_HOURS
    # ---------------- FEDERAL HOLIDAYS (IMPLICIT HOURS) ----------------
    
        # ---------------- STORY / SIGNIFICANCE ----------------
    if any(w in q for w in [
        "story", "significance", "meaning", "why is", "why do we",
        "importance", "about", "legend"
    ]):
        # Avoid date queries like "when is", "dates"
        if not any(w in q for w in ["date", "dates", "when", "time", "timing"]):
            return Intent.STORY

    # ---------------- EVENTS TODAY (HIGH PRIORITY) ----------------    
    if is_events_today(q):
        return Intent.EVENTS_TODAY
    
    # ---------------- SATYANARAYANA POOJA (HIGH PRIORITY) ----------------
    if normalize_satyanarayana(q):
        return Intent.SATYANARAYANA_POOJA



    # ---------------- FOOD ----------------
    if any(w in q for w in ["annadanam", "cafeteria", "food", "lunch", "prasadam"]):
        return Intent.FOOD

    # ---------------- TEMPLE HOURS ----------------
    if any(w in q for w in ["open", "close", "hours", "timing"]):
        return Intent.TEMPLE_HOURS

    # ---------------- LOCATION ----------------
    if any(w in q for w in ["address", "location", "where is", "directions"]):
        return Intent.LOCATION

    # ---------------- PANCHANG ----------------
    # ---------------- LUNAR DATES (POORNIMA / AMAVASYA) ----------------
    if any(w in q for w in ["poornima", "purnima", "amavasya", "new moon", "full moon"]):
        return Intent.LUNAR_DATES

    # ---------------- PANCHANG ----------------
    if any(w in q for w in ["panchang", "tithi", "nakshatra", "star"]):
        if "tomorrow" in q:
            return Intent.PANCHANG_TOMORROW
        if any(m in q for m in [
            "jan","feb","mar","apr","may","jun",
            "jul","aug","sep","oct","nov","dec"
        ]) or any(c.isdigit() for c in q):
            return Intent.PANCHANG_DATE
        return Intent.PANCHANG_TODAY
    
    # ---------------- HOMAMS ----------------
    if "homam" in q:
        if any(w in q for w in ["items", "required", "samagri"]):
            return Intent.HOMAM_ITEMS
        return Intent.HOMAMS

    # ---------------- ABHISHEKAM ----------------
    if "abhishekam" in q:
        if any(w in q for w in ["sponsor", "sponsorship", "amount", "cost"]):
            return Intent.ABHISHEKAM_SPONSORSHIP
        return Intent.WEEKLY_ABHISHEKAM 
    
    # ---------------- KALYANAM ----------------
    if "kalyanam" in q:
        if any(w in q for w in ["sponsor", "sponsorship", "amount", "cost", "price"]):
            return Intent.ABHISHEKAM_SPONSORSHIP
        return Intent.WEEKLY_ABHISHEKAM

    # ---------------- ARJITHA ----------------
    if "arjitha" in q:
        return Intent.ARJITHA_SEVA

    # ---------------- VAHANA ----------------
    if any(w in q for w in ["vahana", "vehicle", "car pooja"]):
        return Intent.VAHANA_POOJA

    # ---------------- EVENTS / POOJA SCHEDULE ----------------
    # ---------------- SUPRABHATA SEVA ----------------
    if "suprabhata" in q:
        return Intent.DAILY_POOJA

    if "daily pooja" in q:
        return Intent.DAILY_POOJA

    if "weekly pooja" in q:
        return Intent.WEEKLY_POOJA

    if "yearly pooja" in q:
        return Intent.YEARLY_POOJA
    
     # ---------------- RELATIVE EVENTS (TOMORROW / WEEKEND) ----------------
    if any(w in q for w in [
        "tomorrow", "tomo", "tmrw",
        "weekend", "this saturday", "this sunday",
        "next saturday", "next sunday"
    ]):
        return Intent.EVENTS_RELATIVE
    
    if any(w in q for w in ["event", "events", "festival", "festivals"]):

    # 🔥 UPCOMING HAS HIGHEST PRIORITY
        if "upcoming" in q or "next" in q:
            return Intent.EVENTS_UPCOMING

        # TODAY
        if "today" in q or "happening" in q:
            return Intent.EVENTS_TODAY

        # YEAR
        if re.search(r"\b20\d{2}\b", q):
            return Intent.EVENTS_YEARLY

        # MONTH
        if any(m in q for m in [
            "january","february","march","april","may","june",
            "july","august","september","october","november","december",
            "jan","feb","mar","apr","jun","jul","aug","sep","oct","nov","dec"
        ]):
            return Intent.EVENTS_MONTHLY

        # WEEK
        if "weekly" in q or "this week" in q:
            return Intent.EVENTS_WEEKLY

        return Intent.EVENTS_MONTHLY



    # ---------------- CONTACTS ----------------
    if any(w in q for w in ["contact", "phone", "email", "manager"]):
        return Intent.CONTACTS

    # ---------------- COMMITTEE ----------------
    if any(w in q for w in ["committee", "board", "trustee"]):
        return Intent.COMMITTEE

    # ---------------- CULTURAL ----------------
    if any(w in q for w in ["dance", "music", "bhajan", "concert", "cultural"]):
        return Intent.CULTURAL

    return Intent.RAG_FALLBACK

def handle_satyanarayana_pooja(q: str, now: datetime) -> str | None:
    q = q.lower()

    if not normalize_satyanarayana(q):
        return None

    # -------------------------------------------------
    # 1️⃣ ITEMS REQUIRED (HIGH PRIORITY)
    # -------------------------------------------------
    if any(w in q for w in ["item", "items", "required", "bring", "samagri", "material"]):
        info = ITEMS_REQUIRED["satyanarayana"]

        return (
            "🪔 SRI SATYANARAYANA SWAMY POOJA – ITEMS REQUIRED\n\n"
            f"{info['items']}\n\n"
            f"📌 NOTE:\n"
            f"• {info['note']}\n"
            f"🔗 {POOJA_SAMAGRI_URL}\n\n"
            + temple_manager_contact()
        )

    # -------------------------------------------------
    # 2️⃣ TIMING + SPONSORSHIP (DEFAULT)
    # -------------------------------------------------
    timing = "• Full Moon Day – 06:30 PM"

    sponsorship = (
        "💰 SPONSORSHIP OPTIONS:\n\n"
        "• Individual Pooja (at Temple): $151\n"
        "• Individual Pooja (at Home): $251\n"
        "• Saamoohika / Group Pooja (at Temple): $116 per family"
    )

    return (
        "🪔 SRI SATYANARAYANA SWAMY POOJA\n\n"
        "📅 TIMING:\n"
        f"{timing}\n\n"
        f"{sponsorship}\n\n"
        + temple_manager_contact()
    )


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


def load_lunar_dates(year: int, lunar_type: str) -> list[str]:
    """
    lunar_type: 'Fullmoon' or 'Amavasya'
    """
    base = os.path.join(
        "data_raw",
        "Events",
        str(year),
        lunar_type
    )

    if not os.path.isdir(base):
        logger.error("Lunar directory not found: %s", base)
        return []

    results = []

    for fname in os.listdir(base):
        if not fname.endswith(".txt"):
            continue

        path = os.path.join(base, fname)
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    clean = line.strip()
                    if clean:
                        results.append(clean)
        except Exception as e:
            logger.error("Error reading lunar file %s", path, exc_info=True)

    return results


def handle_lunar_dates(q: str, now: datetime) -> str | None:
    year = _get_year(now, q)

    is_poornima = any(w in q for w in ["poornima", "purnima", "full moon"])
    is_amavasya = any(w in q for w in ["amavasya", "new moon", "no moon"])

    if not (is_poornima or is_amavasya):
        return None

    months = [
        "january","february","march","april","may","june",
        "july","august","september","october","november","december"
    ]

    target_month = next((m for m in months if m in q), None)

    # -------------------------------
    # LOAD DATA
    # -------------------------------
    if is_poornima:
        raw_dates = load_lunar_dates(year, "Fullmoon")
        title = "🌕 POORNIMA DATES"
    else:
        raw_dates = load_lunar_dates(year, "Amavasya")
        title = "🌑 AMAVASYA DATES"

    if not raw_dates:
        return (
            f"{title} ({year})\n"
            "• Dates not listed.\n\n"
            + temple_manager_contact()
        )

    # -------------------------------
    # MONTH FILTER
    # -------------------------------
    if target_month:
        raw_dates = [
            d for d in raw_dates
            if target_month.capitalize() in d
        ]

    if not raw_dates:
        return (
            f"{title} ({target_month.capitalize()} {year})\n"
            "• No dates listed.\n\n"
            + temple_manager_contact()
        )

    suffix = (
        f" ({target_month.capitalize()} {year})"
        if target_month else f" ({year})"
    )

    lines = [title + suffix]
    for d in raw_dates:
        lines.append(f"• {d}")

    lines.append(temple_manager_contact())
    return "\n".join(lines)



# ============================================================
# STORY INTENT MAPPING
# ============================================================

STORY_INTENT_MAP = [
    ("varalakshmi vratham", "Rituals/Varalakshmi_Vratham.txt"),
    ("varalakshmi", "Rituals/Varalakshmi_Vratham.txt"),
    ("guru poornima", "Rituals/Guru_Poornima.txt"),
    ("guru purnima", "Rituals/Guru_Poornima.txt"),
    ("mahalakshmi jayanthi", "Rituals/Mahalakshmi_Jayanthi.txt"),
    ("mahalakshmi jayanti", "Rituals/Mahalakshmi_Jayanthi.txt"),
    ("diwali", "Rituals/story_of_Diwali.txt"),
    ("deepavali", "Rituals/story_of_Diwali.txt"),
]

def handle_story_query(q: str) -> str | None:
    """Handle story queries by loading from Rituals directory"""
    q = normalize_intent(q)
    
    for key, filename in STORY_INTENT_MAP:
        if key in q and any(w in q for w in ["story", "significance", "meaning", "why", "about"]) \
            and not any(w in q for w in ["date", "dates", "when"]):
            # Correct path with Rituals already in filename
            path = os.path.join("data_raw", filename)
            
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                        if content:
                            return _format_bullets(content)
                except Exception as e:
                    print(f"Error reading {path}: {e}")
            else:
                print(f"Story file not found: {path}")
    
    return None

def temple_manager_contact() -> str:
    return (
        "\n📞 TEMPLE MANAGER CONTACT:\n"
        f"• Phone: {TEMPLE_INFO['Temple_Manager']}\n"
        f"• Email: {TEMPLE_INFO['email']}"
    )
def append_manager_for_details(out: str) -> str:
    """
    Appends a professional Temple Manager contact line
    for detailed / administrative / ceremonial queries.
    """
    return (
        f"{out}\n\n"
        "For detailed information or further clarification, please contact the Temple Manager:\n"
        f"• Phone: {TEMPLE_INFO['Temple_Manager']}\n"
        f"• Email: {TEMPLE_INFO['email']}"
    )

def get_panchang_file(year: int, month: str) -> list[str]:
    """
    Returns all possible panchang file paths for a given year + month
    """
    base = os.path.join("data_raw", "Panchang", str(year))
    return [
           os.path.join(base, f"{month.lower()}_{year}_panchang.txt"),
    ]
def parse_explicit_date(q: str, now: datetime) -> datetime | None:
    """
    Parses queries like:
    - jan 22
    - jan 22nd
    - jan 22 2026
    - jan 22nd 2026
    """
    months = {
        "jan": 1, "january": 1,
        "feb": 2, "february": 2,
        "mar": 3, "march": 3,
        "apr": 4, "april": 4,
        "may": 5,
        "jun": 6, "june": 6,
        "jul": 7, "july": 7,
        "aug": 8, "august": 8,
        "sep": 9, "september": 9,
        "oct": 10, "october": 10,
        "nov": 11, "november": 11,
        "dec": 12, "december": 12,
    }

    for name, month_num in months.items():
        if name in q:
            day_match = re.search(r"\b(\d{1,2})(st|nd|rd|th)?\b", q)
            if not day_match:
                continue

            day = int(day_match.group(1))

            year_match = re.search(r"\b(20\d{2})\b", q)
            year = int(year_match.group(1)) if year_match else now.year

            try:
                return datetime(year, month_num, day, tzinfo=now.tzinfo)
            except ValueError:
                return None

    return None

def get_today_panchang(now: datetime) -> list[str]:
    year = now.year
    month_full = now.strftime("%B").lower()
    month_abbr = now.strftime("%b").lower()
    day = now.day

    base = os.path.join("data_raw", "Panchang", str(year))
    file_path = os.path.join(base, f"{month_full}_{year}_panchang.txt")

    if not os.path.exists(file_path):
        logger.error("Panchang file not found: %s", file_path)
        return []

    with open(file_path, "r", encoding="utf-8") as f:
        rows = f.readlines()

    results = []
    capture = False

    date_re = re.compile(
        rf"\b({month_abbr}|{month_full})\s+0*{day}(st|nd|rd|th)?\b",
        re.IGNORECASE
    )

    next_date_re = re.compile(
        rf"\b({month_abbr}|{month_full})\s+\d{{1,2}}",
        re.IGNORECASE
    )

    paksham = None

    for row in rows:
        clean = row.strip()

        if date_re.search(clean):
            capture = True
            results.append(clean)
            continue

        if capture:
            if next_date_re.search(clean):
                break

            # TITHI LINE
            if "tithi" in clean.lower():
                results.append(clean)

                inferred = infer_paksham_from_tithi(clean)
                if inferred:
                    paksham = inferred

            # OTHER LINES
            elif any(k in clean.lower() for k in [
                "nakshatra", "event:"
            ]):
                results.append(clean)

    if paksham:
        results.insert(1, f"Paksham: {paksham}")

    return results



def handle_panchang(q: str, now: datetime) -> str | None:
    if not any(w in q for w in ["panchang", "tithi", "nakshatra", "star", "maasa", "paksham"]):
        return None

    explicit_date = parse_explicit_date(q, now)

    if explicit_date:
        target_date = explicit_date
        label = target_date.strftime("%B %d, %Y")
    elif any(w in q for w in ["tomorrow", "tomo"]):
        target_date = now + timedelta(days=1)
        label = "Tomorrow"
    else:
        target_date = now
        label = "Today"

    lines = get_today_panchang(target_date)

    maasa_info = get_maasa_paksham(target_date.date())
    logger.info("maasa paksham %s", maasa_info)
    maasa_line = ""
    if maasa_info:
        maasa, paksham = maasa_info
        maasa_line = f"🪔 Maasa: {maasa}\n🌗 Paksham: {paksham}\n"

    if not lines:
        return f"🌙 {label}'s Panchang is not listed."

    # Intent filters
    if "tithi" in q:
        filtered = [l for l in lines if "tithi" in l.lower()]
        if filtered:
            return (
                f"🌙 {label}'s Tithi\n"
                f"{maasa_line}"
                + "\n".join(f"• {l}" for l in filtered)
            )

    if "nakshatra" in q or "star" in q:
        filtered = [l for l in lines if "nakshatra" in l.lower()]
        if filtered:
            return (
                f"🌙 {label}'s Nakshatra\n"
                f"{maasa_line}"
                + "\n".join(f"• {l}" for l in filtered)
            )

    # Full Panchang
    out = [
        f"🌙 {label}'s Panchang ({target_date:%B %d, %Y})",
        maasa_line.rstrip(),
    ]
    out.extend(f"• {l}" for l in lines)
    return "\n".join(out)




def get_nth_weekday_of_month(date: datetime) -> tuple[str, str]:
    """
    Returns:
    - ordinal: '1st', '2nd', '3rd', '4th', '5th'
    - weekday: 'Saturday', 'Sunday', etc.
    """
    week_number = (date.day - 1) // 7 + 1
    ordinal_map = {1: "1st", 2: "2nd", 3: "3rd", 4: "4th", 5: "5th"}
    ordinal = ordinal_map.get(week_number, "")
    weekday = date.strftime("%A")
    return ordinal, weekday

def get_today_special_events(now: datetime) -> List[str]:
    month = now.strftime("%B")
    day = now.day
    year = now.year
    
    LAMBDA_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logger.info("root dir %s", LAMBDA_ROOT)
    events_file = os.path.join(
        LAMBDA_ROOT,
        "data_raw",
        "Events",
        str(year),
        f"{month}_{year}_Events.txt"
    )
    logger.info("file for events %s",events_file)

    if not os.path.isfile(events_file):
        print(f"Error!! file {events_file} not found")
        return []

    with open(events_file, "r", encoding="utf-8") as f:
        lines = [l.rstrip() for l in f]

    header_pattern = re.compile(
        rf"{month}\s+{day},\s*{year}\s*[-]\s*(.+)",
        re.IGNORECASE
    )
    logger.info("header pattern arrived %s",header_pattern)
    results: List[str] = []
    capture = False

    for line in lines:
        clean = line.strip()

        # Start capture at today's header
        m = header_pattern.match(clean)
        if m:
            capture = True
            results.append(m.group(1).strip())  # Event title
            continue

        # Stop capture at divider or next event header
        if capture:
            if clean.startswith("════"):
                break
            if clean:
                results.append(clean)

        
    return results

def handle_today_events(q: str, now: datetime) -> str | None:
    logger.info("query-%s",q)
    logger.info("i m in today handler")

    if any(w in q for w in ["panchang", "tithi", "nakshatra", "star"]):
        return None
  
    ordinal, weekday = get_nth_weekday_of_month(now)

    lines = [
        f"📅 TODAY: {now:%A, %B %d, %Y}",
        ""
    ]

    # 🔥 1️⃣ SPECIAL EVENTS FIRST (AUTHORITATIVE)
    special_events = get_today_special_events(now)
    logger.info("special events- %s",special_events)
    if special_events:
        lines.append("🎉 SPECIAL EVENTS TODAY:")
        for ev in special_events:
            lines.append(f"• {ev}" if not ev.startswith("•") else ev)
        lines.append("")  # spacing
    
    
    # 🪔 3️⃣ ABHISHEKAM TODAY (ONLY IF MATCHES)
    abhishekams_today = [
        s for k, s in WEEKLY_EVENTS.items()
        if "abhishekam" in k
        and s.startswith(f"{ordinal} {weekday}")
    ]

    if abhishekams_today:
        lines.append("")
        lines.append("🪔 ABHISHEKAM TODAY:")
        for a in abhishekams_today:
            lines.append(f"• {a}")
         

    # 🪔 2️⃣ DAILY POOJA (ALWAYS VALID)
    lines.append("📿 DAILY POOJA:")
    for d in DAILY_SCHEDULE:
        lines.append(f"• {d}")

    # 🪔 3️⃣ WEEKLY EVENTS (ONLY IF TODAY MATCHES)
    
    weekly = [
        s for s in WEEKLY_EVENTS.values()
        if s.startswith(f"{ordinal} {weekday}")
    ]

    if weekly:
        lines.append("")
        lines.append("🪔 WEEKLY EVENTS TODAY:")
        for w in weekly:
            lines.append(f"• {w}")
  
    # 🌙 4️⃣ PANCHANG
    panchang = get_today_panchang(now)
    if panchang:
        lines.append("")
        lines.append("🌙 TODAY'S PANCHANG:")
        for p in panchang:
            lines.append(f"• {p}")

    lines.append("")
    lines.append(temple_manager_contact())

    return "\n".join(lines)

def get_year_events(year: int) -> list[tuple[datetime, str]]:
    base = os.path.join("data_raw", "Events", str(year))
    logger.info("file location in get year events %s", base)
    events = []

    if not os.path.isdir(base):
        return []

    header_re = re.compile(
    r"([A-Za-z]+)\s+(\d{1,2})(?:st|nd|rd|th)?,\s*(\d{4})\s*-\s*(.+)",
    re.IGNORECASE
)


    for fname in os.listdir(base):
        if not fname.endswith("_Events.txt"):
            continue

        path = os.path.join(base, fname)

        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                m = header_re.match(line.strip())
                if not m:
                    continue

                month, day, year_s, title = m.groups()
                try:
                    dt = datetime.strptime(
                        f"{month} {day} {year_s}",
                        "%B %d %Y"
                    )
                except ValueError:
                    continue

                events.append((dt, title.strip()))

    # 🔥 SORT CHRONOLOGICALLY
    events.sort(key=lambda x: x[0])
    logger.info("events extracted %s", events)
    return events

def handle_location(q: str, now: datetime) -> str | None:
    if not any(w in q for w in ["address", "location", "where is", "directions"]):
        return None

    return (
        "📍 SRI VENKATESWARA TEMPLE – LOCATION\n\n"
        f"• Address: {TEMPLE_INFO['address']}\n"
        "• City: Castle Rock, Colorado\n"
        "• Parking available on-site\n\n"
        + temple_manager_contact()
    )


def handle_homam(q: str, now: datetime) -> str | None:

    if any(w in q for w in ["item", "items", "required", "bring", "samagri", "material"]):
        return None
    if "homam" not in q:
        return None

    q = q.lower()

    # -------------------------
    # SPECIFIC HOMAMS (NAME-BASED)
    # -------------------------
    if "ayush" in q:
        return (
            "🪔 AYUSH HOMAM – SPONSORSHIP\n\n"
            "• At Temple: $151\n"
            "• At Home: $201\n\n"
            + temple_manager_contact()
        )

    if "chandi" in q:
        return (
            "🪔 CHANDI HOMAM – SPONSORSHIP\n\n"
            "• At Temple: $401\n"
            "• At Home: $501\n\n"
            + temple_manager_contact()
        )

    if "sudarshana" in q:
        return (
            "🪔 SUDARSHANA HOMAM (SAAMOOHIKA)\n\n"
            "• 4th Sunday 11:00 AM\n"
            "• Sponsorship per family: $51\n\n"
            + temple_manager_contact()
        )

    # -------------------------
    # LIST
    # -------------------------
    if any(w in q for w in ["list", "types", "available"]):
        return homam_list_response()

    # -------------------------
    # COST / SPONSORSHIP
    # -------------------------
    if any(w in q for w in ["cost", "price", "sponsorship", "how much"]):
        return homam_cost_response(q)

    # -------------------------
    # DEFAULT
    # -------------------------
    return (
        "🪔 HOMAM (Fire Ritual)\n\n"
        "• Homams are Vedic fire rituals performed for health, prosperity, and spiritual upliftment\n"
        "• Available at the temple or at home (by prior booking)\n\n"
        + temple_manager_contact()
    )

def handle_items_required(q: str, now: datetime) -> str | None:
    if not any(w in q for w in ["item", "items", "bring", "required", "need", "samagri", "material"]):
        return None

    # --------------------------------------------------
    # 1️⃣ ANY DEITY ABHISHEKAM → SAME ITEMS
    # --------------------------------------------------
    if "abhishekam" in q:
        info = ITEMS_REQUIRED["abhishekam"]
        return (
            "Om Namo Venkateshaya 🙏\n\n"
            "🪔 ITEMS REQUIRED FOR ABHISHEKAM\n\n"
            f"{info['items']}\n\n"
            "📌 These items are COMMON for ALL Abhishekams:\n"
            "• Siva Abhishekam\n"
            "• Ganapati Abhishekam\n"
            "• Murugan Abhishekam\n"
            "• Hanuman Abhishekam\n"
            "• Sai Baba Abhishekam\n"
            "• Raghavendra Swamy Abhishekam\n"
            "• Venkateswara Swamy Abhishekam\n\n"
            f"📌 {info['note']}\n"
            f"🔗 {POOJA_SAMAGRI_URL}\n\n"
            + temple_manager_contact()
        )

    # --------------------------------------------------
    # 2️⃣ DIRECT ITEM KEYS (Satyanarayana, Gruhapravesam, etc.)
    # --------------------------------------------------
    for phrase, key in ITEM_KEYS.items():
        if phrase in q:
            info = ITEMS_REQUIRED[key]
            return (
                "Om Namo Venkateshaya 🙏\n\n"
                f"🪔 {info['name'].upper()}\n\n"
                f"{info['items']}\n\n"
                f"📌 {info['note']}\n"
                f"🔗 {POOJA_SAMAGRI_URL}\n\n"
                + temple_manager_contact()
            )

    # --------------------------------------------------
    # 3️⃣ FALLBACK – SHOW VALID OPTIONS (NO GENERIC GARBAGE)
    # --------------------------------------------------
    valid = sorted([

        "Abhishekam (all deities)",
        "Satyanarayana Pooja",
        "Homam",
        "Sudarshana Homam",
        "Vastu Pooja",
        "Nava Graha Pooja",

        # Life events / samskaras
        "Gruhapravesam",
        "Bhoomi Pooja",
        "Hindu Wedding",
        "Engagement (Nischitartham)",
        "Kalyanam",
        "Half Saree Function",
        "Aksharabhyasam",
        "Namakaranam",
        "Annaprasana",
        "Seemantham",
        "Hair Offering (Mundan)",
        "Hiranya Shraddham",
    ])

    return (
        "Om Namo Venkateshaya 🙏\n\n"
        "🪔 POOJA ITEMS INFORMATION\n\n"
        "Please specify one of the following:\n\n"
        + "\n".join(f"• {v}" for v in valid)
        + "\n\n"
        + temple_manager_contact()
    )


def handle_arjitha_seva(q: str, now: datetime) -> str | None:
    if "arjitha" not in q:
        return None

    if any(w in q for w in ["what is", "meaning", "explain"]):
        return (
            "🪔 ARJITHA SEVA\n\n"
            "• Arjitha Seva is a special priest-performed service requested by individual devotees\n"
            "• Includes Abhishekam, Archana, Homam, Vrathams, and life-event ceremonies\n\n"
            + temple_manager_contact()
        )

    if any(w in q for w in ["list", "types", "available"]):
        return (
            "🪔 ARJITHA SEVAS AVAILABLE\n\n"
            "• Abhishekam\n"
            "• Archana\n"
            "• Homams\n"
            "• Vrathams\n"
            "• Life-event ceremonies (Samskaras)\n\n"
            + temple_manager_contact()
        )

    if any(w in q for w in ["how", "book", "schedule"]):
        return (
            "🪔 HOW TO BOOK ARJITHA SEVA\n\n"
            "• Decide the seva type\n"
            "• Choose temple or home\n"
            "• Contact temple to confirm date and priest availability\n\n"
            + temple_manager_contact()
        )
    return (
            "🪔 ARJITHA SEVA\n\n"
            "• Arjitha Seva is a special priest-performed service requested by individual devotees\n"
            "• Includes Abhishekam, Archana, Homam, Vrathams, and life-event ceremonies\n\n"
            "• Do you want to book any abhishekams, archana, homams or life -event ceremonies\n\n"
            + temple_manager_contact()
        )  

    
def handle_vahana_pooja(q: str, now: datetime) -> str | None:
    if not any(w in q for w in ["vahana", "vehicle", "car pooja"]):
        return None

    return (
        "🚗 VAHANA POOJA\n\n"
        "• Walk-ins are welcome subject to priest availability\n"
        "• Bring: 4 lemons, 1 coconut, fruits, and flowers\n\n"
        + temple_manager_contact()
    )

def is_new_year(day: datetime) -> bool:
    return day.month == 1 and day.day == 1


def is_independence_day(day: datetime) -> bool:
    return day.month == 7 and day.day == 4


def is_christmas(day: datetime) -> bool:
    return day.month == 12 and day.day == 25


def is_memorial_day(day: datetime) -> bool:
    # Last Monday of May
    if day.month != 5 or day.weekday() != 0:
        return False
    return (day + timedelta(days=7)).month != 5


def is_labor_day(day: datetime) -> bool:
    # First Monday of September
    return day.month == 9 and day.weekday() == 0 and day.day <= 7


def is_thanksgiving(day: datetime) -> bool:
    # Fourth Thursday of November
    return (
        day.month == 11
        and day.weekday() == 3  # Thursday
        and 22 <= day.day <= 28
    )

def is_supported_federal_holiday(now: datetime) -> tuple[bool, str | None]:
    if is_new_year(now):
        return True, "New Year’s Day"
    if is_memorial_day(now):
        return True, "Memorial Day"
    if is_independence_day(now):
        return True, "Independence Day"
    if is_labor_day(now):
        return True, "Labor Day"
    if is_thanksgiving(now):
        return True, "Thanksgiving Day"
    if is_christmas(now):
        return True, "Christmas Day"
    # Martin Luther King Jr. Day – Third Monday of January
    if now.month == 1 and now.weekday() == 0 and 15 <= now.day <= 21:
        return True, "Martin Luther King Jr. Day"


    return False, None


def handle_temple_hours(q: str, now: datetime) -> str | None:
    current_time = now.time()
    is_weekend = now.weekday() >= 5
    is_holiday, holiday_name = is_supported_federal_holiday(now)

    q= q.lower()

    if is_full_day_open_holiday_query(q):
        return (
            f"🕉️ TEMPLE STATUS: OPEN FULL DAY (Federal Holiday – {holiday_name})\n\n"
            "• Holiday hours: 9:00 AM – 8:00 PM\n"
            "• The temple remains open throughout the day\n\n"
            + temple_manager_contact()
        )
    # -----------------------------
    # TIME DEFINITIONS
    # -----------------------------
    weekday_morning = (time(9, 0), time(12, 0))
    weekday_evening = (time(18, 0), time(20, 0))
    full_day = (time(9, 0), time(20, 0))

    def in_slot(start, end):
        return start <= current_time <= end
    
    if not any(w in q for w in ["open", "close", "hours", "timing"]):
        return None
    # -----------------------------
    # WEEKEND OR HOLIDAY → FULL DAY
    # -----------------------------
    if is_weekend or is_holiday:
        if is_holiday:
            label = f"Federal Holiday – {holiday_name}"
            holiday_note = "• Today is a federal holiday.\n"
        else:
            label = "Weekend"
            holiday_note = ""

        if in_slot(*full_day):
            return (
                f"🕉️ TEMPLE STATUS: OPEN NOW ({label})\n\n"
                f"{holiday_note}"
                "• Temple hours: 9:00 AM – 8:00 PM\n\n"
                + temple_manager_contact()
            )
        else:
            return (
                f"🕉️ TEMPLE STATUS: CLOSED NOW ({label})\n\n"
                f"{holiday_note}"
                "• Temple hours: 9:00 AM – 8:00 PM\n"
                "• Next opening: 9:00 AM\n\n"
                + temple_manager_contact()
            )
    # -----------------------------
    # WEEKDAY LOGIC
    # -----------------------------
    if in_slot(*weekday_morning) or in_slot(*weekday_evening):
        return (
            "🕉️ TEMPLE STATUS: OPEN NOW\n\n"
            "• Weekday hours:\n"
            "  – 9:00 AM – 12:00 PM\n"
            "  – 6:00 PM – 8:00 PM\n\n"
            + temple_manager_contact()
        )

    # -----------------------------
    # WEEKDAY CLOSED
    # -----------------------------
    if current_time < time(9, 0):
        next_open = "9:00 AM today"
    elif current_time < time(18, 0):
        next_open = "6:00 PM today"
    else:
        next_open = "9:00 AM tomorrow"

    return (
        "🕉️ TEMPLE STATUS: CLOSED NOW\n\n"
        "• Weekday hours:\n"
        "  – 9:00 AM – 12:00 PM\n"
        "  – 6:00 PM – 8:00 PM\n"
        f"• Next opening: {next_open}\n\n"
        + temple_manager_contact()
    )



def handle_contacts(q: str, now: datetime) -> str | None:
    if not any(w in q for w in ["contact", "phone", "email", "call"]):
        return None

    if "manager" in q:
        return temple_manager_contact()

    if "chairman" in q:
        return f"• Chairman: {TEMPLE_INFO['contacts']['chairman']}"

    if "president" in q:
        return f"• President: {TEMPLE_INFO['contacts']['president']}"

    return temple_manager_contact()

def handle_committee_queries(q: str, now: datetime) -> str | None:
    if not any(w in q for w in ["committee", "board", "trustee", "leadership"]):
        return None

    lines = ["🏛️ TEMPLE COMMITTEES:\n"]
    for c in TEMPLE_INFO["committees"].values():
        lines.append(f"• {c}")

    lines.append(temple_manager_contact())
    return "\n".join(lines)

def handle_cultural_programs(q: str, now: datetime) -> str | None:
    if not any(w in q for w in ["dance", "music", "bhajan", "concert", "performance", "cultural"]):
        return None

    return (
        "🎶 CULTURAL & DEVOTIONAL PROGRAMS\n\n"
        "• Dance, music, bhajans, and cultural programs are welcome\n"
        "• Prior approval and scheduling required\n\n"
        + temple_manager_contact()
    )

def handle_story(q: str, now: datetime) -> str | None:
    return handle_story_query(q)

def generic_weekly_abhishekam_list() -> str:
    lines = ["🪔 WEEKLY ABHISHEKAM SCHEDULE\n"]

    for key, schedule in WEEKLY_EVENTS.items():
        display = DISPLAY_WEEKLY_NAMES.get(key, key.title())
        lines.append(f"• {schedule.replace('–', '– ' + display)}")

    lines.append(temple_manager_contact())
    return "\n".join(lines)


def handle_weekly_abhishekam(q: str, now: datetime) -> str | None:
    q = q.lower().strip()

    # Ignore item/material queries
    if any(w in q for w in ["item", "items", "required", "bring", "samagri", "material"]):
        return None

    if "homam" in q:
        return None

    ordinal, weekday = get_nth_weekday_of_month(now)
    today_key = f"{ordinal} {weekday}"

    matched = None
    is_generic_weekly = "weekly pooja" in q or "weekly poojas" in q

    # -------------------------------------------------
    # 1️⃣ VENKATESWARA KALYANAM (SPECIAL CASE)
    # -------------------------------------------------
    if "kalyanam" in q and "venkateswara" in q:
        sched = WEEKLY_EVENTS["venkateswara swamy kalyanam"]
        happening_today = sched.startswith(today_key)

        return "\n".join([
            "🪔 Sri Venkateswara Swamy Kalyanam",
            "",
            f"• {sched}",
            f"• {'HAPPENING TODAY' if happening_today else 'Not today'}",
            "",
            WEEKLY_SPONSORSHIP["venkateswara swamy kalyanam"],
            "",
            temple_manager_contact()
        ])

    # -------------------------------------------------
    # 2️⃣ GENERIC WEEKLY POOJA LIST
    # -------------------------------------------------
    if is_generic_weekly and "abhishekam" not in q:
        lines = ["🪔 WEEKLY TEMPLE POOJAS\n"]

        for key, sched in WEEKLY_EVENTS.items():
            display = DISPLAY_WEEKLY_NAMES.get(key, key.title())
            is_today = sched.startswith(today_key)

            status = "✅ Today" if is_today else f"📅 {sched.split('–')[0].strip()}"
            lines.append(f"• {display}: {status}")

        lines.append("\n" + temple_manager_contact())
        return "\n".join(lines)

    # -------------------------------------------------
    # 3️⃣ DEITY-SPECIFIC ABHISHEKAM MATCHING
    # -------------------------------------------------
    if "abhishekam" in q:
        if any(k in q for k in ["venkateswara", "venkateshwara", "balaji", "tirupati"]):
            matched = "venkateswara swamy abhishekam"
        elif "siva" in q:
            matched = "siva abhishekam"
        elif "murugan" in q or "subramanya" in q:
            matched = "murugan abhishekam"
        elif "ganapati" in q or "ganesha" in q:
            matched = "ganapati abhishekam"
        elif "hanuman" in q:
            matched = "hanuman abhishekam"
        elif "sai" in q:
            matched = "sai baba abhishekam"
        elif "raghavendra" in q:
            matched = "raghavendra swamy abhishekam"

    # Canonical fallback
    if matched is None and "abhishekam" in q:
        for phrase, canonical in CANONICAL_WEEKLY_KEYS.items():
            if phrase in q:
                matched = canonical
                break

    # -------------------------------------------------
    # 4️⃣ SAFE FALLBACK
    # -------------------------------------------------
    if "abhishekam" in q and matched is None:
        return (
            "🪔 WEEKLY ABHISHEKAMS AT THE TEMPLE\n\n"
            "Please specify the deity name (e.g., Siva, Hanuman, Murugan).\n\n"
            + temple_manager_contact()
        )

    if matched is None:
        return None

    # -------------------------------------------------
    # 5️⃣ FINAL RESPONSE WITH TODAY CHECK
    # -------------------------------------------------
    schedule = WEEKLY_EVENTS.get(matched)
    sponsorship = WEEKLY_SPONSORSHIP.get(matched, "")
    display = DISPLAY_WEEKLY_NAMES.get(matched, matched.title())

    happening_today = schedule.startswith(today_key)

    response = [
        f"🪔 {display}",
        "",
        f"• {schedule}",
        f"• {'HAPPENING TODAY' if happening_today else 'Not today'}",
    ]

    if sponsorship:
        response.extend(["", sponsorship])

    response.append(temple_manager_contact())
    return "\n".join(response)




def handle_daily_pooja(q: str, now: datetime) -> str | None:
    if "suprabhata" in q:
        return (
            "🪔 SRI VENKATESWARA SUPRABHATA SEVA\n\n"
            "• Time: 09:00 AM\n"
            "• Performed daily at the temple\n"
            "• Marks the ceremonial awakening of Lord Venkateswara\n\n"
            + temple_manager_contact()
        )

    if "daily" in q and "pooja" in q:
        return (
            "📿 DAILY POOJA SCHEDULE\n\n"
            + "\n".join(f"• {s}" for s in DAILY_SCHEDULE)
            + "\n\n"
            + temple_manager_contact()
        )

    return None


def handle_monthly_pooja(q: str, now: datetime) -> str | None:
    
    lines = ["📅 MONTHLY TEMPLE POOJA SCHEDULE\n"]

    # Weekly (recurring)
    lines.append("🪔 WEEKLY POOJAS:")
    for s in WEEKLY_EVENTS.values():
        lines.append(f"• {s}")


    # Monthly specials
    lines.append("\n🌕 MONTHLY SPECIAL EVENTS:")
    for s in MONTHLY_SCHEDULE:
        lines.append(f"• {s}")

    lines.append("\n" + temple_manager_contact())
    return "\n".join(lines)



def finalize(out: str, q: str, include_contact: bool = True) -> str:
    
    if any(k in q for k in MANAGER_ESCALATION_KEYWORDS):
        return append_manager_for_details(out)

    if include_contact and "TEMPLE MANAGER CONTACT" not in out:
        out = f"{out}\n\n{temple_manager_contact()}"

    return out

def is_manager_escalation(q: str) -> bool:
    return any(k in q for k in MANAGER_ESCALATION_KEYWORDS)

def handle_food(q: str, now: datetime) -> str | None:
    day = now.strftime("%A")
    is_weekend = _is_weekend(now)

    # ------------------------------------
    # ANNADANAM / CATERING SPONSORSHIP
    # ------------------------------------
    if any(w in q for w in [
        "annadanam sponsor",
        "annadanam sponsorship",
        "sponsor annadanam",
        "catering",
        "catering service",
        "catering contact",
        "annapoorna",
        "annapurna",
        "food sponsorship"
    ]):
        return (
            "🍽️ ANNADANAM & CATERING SERVICES\n\n"
            "• For Annadanam sponsorship or catering services, please contact:\n"
            f"• {TEMPLE_INFO['contacts']['catering']}\n\n"
            "• Catering is coordinated through the Annapoorna Committee\n"
            "• Advance notice is required"
        )

    # ------------------------------------
    # PRASADAM
    # ------------------------------------
    if "prasadam" in q:
        return (
            "• Prasadam is available during temple poojas\n"
            "• Availability depends on the pooja schedule\n"
            + temple_manager_contact()
        )

    # ------------------------------------
    # ANNADANAM / CAFETERIA / LUNCH
    # ------------------------------------
    if any(w in q for w in ["annadanam", "cafeteria", "food", "lunch", "meal"]):
        if is_weekend:
            return (
                "• Annadanam (temple cafeteria) is available today\n"
                "• Serving time: 12:00 PM – 2:00 PM\n"
                "• Traditional vegetarian meals are served\n\n"
                + temple_manager_contact()
            )
        else:
            return (
                f"• Annadanam is not available today ({day})\n"
                "• Served only on Saturdays & Sundays\n"
                "• Timing: 12:00 PM – 2:00 PM\n\n"
                + temple_manager_contact()
            )

    return None

def normalize_satyanarayana(q: str) -> bool:
    patterns = [
        r"satya\s*narayan",
        r"satya\s*narayanan",
        r"satyanarayan",
        r"satyanarayana",
        r"satyanarayana\s*swamy",
    ]
    return any(re.search(p, q) for p in patterns)

def handle_vedic_recitation(q: str, now: datetime) -> str | None:
    return (
        "🪔 VEDIC RECITATIONS & CHANTING\n\n"
        "• Sukthams, Sahasranamams, and Nama Sankeerthanams "
        "are priest-led services based on availability and temple schedule\n"
        "• Please contact the Temple Manager for timing, booking, or participation details\n\n"
        + temple_manager_contact()
    )


def handle_upcoming_events(q: str, now: datetime) -> str | None:
    year = _get_year(now, q)
    events = get_year_events(year)

    upcoming = [
        (dt, title)
        for dt, title in events
        if dt.date() >= now.date()
    ]

    # Optional: month filter
    months = [
        "january","february","march","april","may","june",
        "july","august","september","october","november","december"
    ]
    target_month = next((m for m in months if m in q), None)

    if target_month:
        upcoming = [
            (dt, title)
            for dt, title in upcoming
            if dt.strftime("%B").lower() == target_month
        ]

    if not upcoming:
        return (
            "📅 UPCOMING EVENTS\n"
            "• No upcoming events listed.\n\n"
            + temple_manager_contact()
        )

    lines = ["📅 UPCOMING EVENTS\n"]
    for dt, title in upcoming:
        lines.append(f"• {dt:%b %d}: {title}")

    lines.append(temple_manager_contact())
    return "\n".join(lines)

def handle_rag_fallback(q: str, now: datetime) -> str | None:
    specified_month = None

    for month in [
        "january","february","march","april","may","june",
        "july","august","september","october","november","december"
    ]:
        if month in q:
            specified_month = month
            break

    is_date_query = any(w in q for w in [
        "full moon", "purnima", "amavasya",
        "ekadasi", "ekadashi", "new moon", "pournami"
    ])

    if not specified_month and is_date_query:
        specified_month = now.strftime("%B").lower()

    # Decide chunk depth
    k_value = 20 if any(w in q for w in [
        "meaning", "what is", "explain", "significance", "why", "about", "story"
    ]) else 10

    try:
        chunks = get_chunks(q, k=k_value)
        if not chunks:
            return None

        texts = []
        seen = set()

        month_abbr_map = {
            'january': 'Jan','february': 'Feb','march': 'Mar','april': 'Apr',
            'may': 'May','june': 'Jun','july': 'Jul','august': 'Aug',
            'september': 'Sep','october': 'Oct','november': 'Nov','december': 'Dec'
        }

        for chunk in chunks:
            text = chunk.get("text", "").strip()
            if len(text) < 20:
                continue

            if is_date_query and specified_month:
                abbr = month_abbr_map.get(specified_month)
                if abbr and abbr not in text and specified_month.capitalize() not in text:
                    continue

            if text not in seen:
                texts.append(text)
                seen.add(text)

        if not texts:
            return None

        context = "\n".join(texts[:7] if k_value == 20 else texts[:5])

        prompt = f"""You are a helpful assistant for Sri Venkateswara Temple in Castle Rock, Colorado.

STRICT RESPONSE RULES (MANDATORY):
1. If the requested information is NOT available in the provided context:
   - DO NOT mention missing context, documents, files, or sources
   - DO NOT explain why the information is unavailable
   - DO NOT say "not found", "not mentioned", "not available", or similar
   - DIRECTLY instruct the user to contact the Temple Manager

2. NEVER use phrases like:
   - "The provided context does not contain"
   -" While the current temple context does not specify"
   - "The documents do not mention"
   - "Based on the available information"
   - "I cannot find"
   - "There is no information"

3. ALWAYS respond in bullet points (•)
4. NEVER apologize
5. NEVER reference files, documents, or context
6. Use a calm, devotional temple tone

Current Date: {now.strftime('%B %d, %Y')}

Temple Information:
{context}

User Question: {q}

Instructions:
- Answer naturally and conversationally based ONLY on the temple information provided in the context
- NEVER add disclaimers like "Note:", "[Note:", "While the context...", or "I cannot provide..., Additional resources, .txt files"
- If you have partial information, share what you have without disclaimers
- ALWAYS use "sponsorship" instead of "cost" or "price" when referring to service fees
- ALWAYS use "donation" instead of "cost" when appropriate
- if sponsorship term is not used when amount is mentioned, add it as prefix and highlight it.
- Keep responses concise, helpful, and complete.
- NEVER apologize or explain missing information
- Do not add any other text. NEVER mention reference file like*.txt file.
- For dates/schedules, be specific with the information provided
- Do not make up information not present in the temple documents
- Answer directly and completely without meta-commentary about sources or missing details

Answer:"""

        client = get_bedrock_client()
        if not client:
            return (
                "• AI assistance is temporarily unavailable.\n\n"
                + temple_manager_contact()
            )
        response = client.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "temperature": 0.3,
                "messages": [{"role": "user", "content": prompt}]
            })
        )

        result = json.loads(response["body"].read())
        raw_text = _sanitize(result["content"][0]["text"])

        FORBIDDEN_PHRASES = [
            "provided temple context",
            "temple context does not",
            "context does not",
            "does not contain",
            "not mentioned",
            "documents focus on",
            "does not provide specific details",
        ]

        lowered = raw_text.lower()

        for phrase in FORBIDDEN_PHRASES:
            if phrase in lowered:
                return (
                    "🪔 For information on recitation, timing, or observance of this prayer at the temple, "
                    "please contact the Temple Manager.\n\n"
                    + temple_manager_contact()
                )

        return raw_text


    except Exception as e:
        logger.error("RAG fallback failed", exc_info=True)
        return (
            "• That information is currently unavailable.\n\n"
            + temple_manager_contact()
        )

MAX_QUERY_LEN = 500

def handle_weekly_events(q: str, now: datetime) -> str | None:
    year = _get_year(now, q)
    events = get_year_events(year)

    start = now.date()
    end = start + timedelta(days=7)

    weekly = [
        (dt, title)
        for dt, title in events
        if start <= dt.date() <= end
    ]

    if not weekly:
        return (
            "📅 EVENTS THIS WEEK\n"
            "• No events scheduled this week.\n\n"
            + temple_manager_contact()
        )

    lines = ["📅 EVENTS THIS WEEK\n"]
    for dt, title in weekly:
        lines.append(f"• {dt:%b %d}: {title}")

    lines.append(temple_manager_contact())
    return "\n".join(lines)

def handle_monthly_events(q: str, now: datetime) -> str | None:
    year = _get_year(now, q)
    events = get_year_events(year)

    months = [
        "january","february","march","april","may","june",
        "july","august","september","october","november","december"
    ]

    target_month = next((m for m in months if m in q), None)
    if not target_month:
        return None

    monthly = [
        (dt, title)
        for dt, title in events
        if dt.strftime("%B").lower() == target_month
    ]

    if not monthly:
        return (
            f"📅 EVENTS IN {target_month.capitalize()} {year}\n"
            "• No events listed.\n\n"
            + temple_manager_contact()
        )

    lines = [f"📅 EVENTS IN {target_month.capitalize()} {year}\n"]
    for dt, title in monthly:
        lines.append(f"• {dt:%b %d}: {title}")

    lines.append(temple_manager_contact())
    return "\n".join(lines)


def handle_year_events(q: str, now: datetime) -> str | None:
    match = re.search(r"\b(20\d{2})\b", q)
    if not match:
        return None

    year = int(match.group(1))
    if year < 2024 or year > now.year + 2:
        return None

    events = get_year_events(year)
    if not events:
        return f"📅 EVENTS FOR {year}\n• No events listed."

    lines = [f"📅 TEMPLE EVENTS – {year}\n"]

    for dt, title in events:
        lines.append(f"• {dt:%b %d}: {title}")

    lines.append(temple_manager_contact())
    return "\n".join(lines)

def infer_paksham_from_tithi(tithi_line: str) -> str | None:
    l = tithi_line.lower()

    if "purnima" in l:
        return "Shukla Paksha"
    if "amavasya" in l:
        return "Krishna Paksha"

    # fallback hints
    if "shukla" in l:
        return "Shukla Paksha"
    if "krishna" in l:
        return "Krishna Paksha"

    return None


INTENT_HANDLERS = {

    Intent.STORY: [handle_story],

    #food
    Intent.FOOD: [handle_food],

    #hours

    Intent.TEMPLE_HOURS: [handle_temple_hours],


    Intent.VEDIC_RECITATION:[handle_vedic_recitation],

    #hours
    Intent.LOCATION: [handle_location],

    #usual schedule
    Intent.DAILY_POOJA: [handle_daily_pooja],
    Intent.WEEKLY_POOJA: [handle_weekly_abhishekam],
    Intent.MONTHLY_POOJA: [handle_monthly_pooja],
    Intent.WEEKLY_ABHISHEKAM: [handle_weekly_abhishekam],
    Intent.ABHISHEKAM_SPONSORSHIP: [handle_weekly_abhishekam],

    #events
    Intent.EVENTS_TODAY: [handle_today_events],
    Intent.EVENTS_WEEKLY: [handle_weekly_events],
    Intent.EVENTS_MONTHLY: [handle_monthly_events],
    Intent.EVENTS_YEARLY: [handle_year_events],
    Intent.EVENTS_UPCOMING: [handle_upcoming_events],
    Intent.EVENTS_RELATIVE: [handle_relative_events],


    #satyanarayana
    Intent.SATYANARAYANA_POOJA: [handle_satyanarayana_pooja],

    #panchang
    Intent.PANCHANG_TODAY: [handle_panchang],
    Intent.PANCHANG_TOMORROW: [handle_panchang],
    Intent.PANCHANG_DATE: [handle_panchang],
    Intent.LUNAR_DATES: [handle_lunar_dates],


    Intent.HOMAMS: [handle_homam],
    Intent.HOMAM_ITEMS: [handle_items_required],

    Intent.ARJITHA_SEVA: [handle_arjitha_seva],
    Intent.VAHANA_POOJA: [handle_vahana_pooja],

    Intent.CONTACTS: [handle_contacts],
    Intent.COMMITTEE: [handle_committee_queries],
    Intent.CULTURAL: [handle_cultural_programs],

    Intent.RAG_FALLBACK: [handle_rag_fallback],
}

def answer_user(query: str, user_id: Optional[str] = None, message_ts: Optional[int] = None):
    if message_ts:
        now = datetime.fromtimestamp(message_ts, ZoneInfo("America/Denver"))
    else:
        now = datetime.now(ZoneInfo("America/Denver"))

    if not query or not isinstance(query, str):
        return "Please provide a valid question."

    # Trim, normalize, limit length (basic injection safety)
    query = query.strip()[:MAX_QUERY_LEN]
    q = normalize_query(query)
    q = autocorrect_query(q)
    q = normalize_intent(q)

    

    intent = classify_intent(q)
    logger.info("Intent=%s | Query=%s", intent.value, q)

    handlers = INTENT_HANDLERS.get(intent, [])
    logger.info("handler %s", handlers)

    for handler in handlers:
        if handler == handle_rag_fallback and is_manager_escalation(q):
            break
        try:
            result= handler(q,now)
            if result:
                return finalize(result,q)
        except Exception:
            logger.error(f"Handler {handler.__name__} failed", exc_info=True)


    return finalize(
        "• I don’t have specific information on that right now.",
        q
    )



        



