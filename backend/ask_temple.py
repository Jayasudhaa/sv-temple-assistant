#backend/ask_temple.py
# ===============================
# Standard Library Imports
# ===============================
import os
import json
import logging
from datetime import datetime
from pathlib import Path
from enum import Enum
from zoneinfo import ZoneInfo
from datetime import date, timedelta
from typing import Optional, List

# ===============================
# AWS / External
# ===============================
import boto3

# ===============================
# Internal Imports
# ===============================
from .retrieval import get_chunks
from backend.food_query import handle_food
from backend.vahana_query import handle_vahana_pooja
from backend.arjitha_seva_query import handle_arjitha_seva
from backend.satyanarayana_query import handle_satyanarayana_pooja
from backend.items_catalog_query import handle_items_required
from backend.temple_info_query import handle_temple_hours
from backend.temple_info_query import handle_vedic_recitation
from backend.temple_info_query import handle_location
from backend.temple_info_query import handle_contacts
from backend.temple_info_query import handle_committee_queries
from backend.temple_info_query import handle_cultural_programs
from backend.story_query import handle_story
from backend.panchangam import handle_panchang
from backend.homams_query import handle_homam
from backend.get_timing import handle_lunar_dates
from backend.get_timing import handle_calendar_events,handle_abhishekam, next_week_range
from backend.kalyanam_queries import handle_kalyanam

from backend.daily_pooja_query import handle_daily_pooja
from backend.calender_2026 import CALENDAR_2026

from backend.utility import (
    normalize_query,
    autocorrect_query,
    normalize_intent,
    finalize,
    _sanitize,
)

MAX_QUERY_LEN= 500

time_words = [
    "today", "tomorrow", "yesterday",
    "this week", "next week", "last week",
    "this month", "this year"
]

calendar_words = [
    "event", "events", "schedule", "happening",
    "activity", "activities", "program", "programs"
]

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
_bedrock_runtime = None

BEDROCK_MODEL_ID = os.getenv(
    "BEDROCK_MODEL_ID",
    "us.anthropic.claude-3-5-haiku-20241022-v1:0"
)

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



BASE_DIR = Path(__file__).resolve().parent.parent

def get_events_between(
    start: date,
    end: date,
    deity: Optional[str] = None
) -> List[date]:
    """
    Returns all abhishekam dates between start and end (inclusive).
    Filters by deity if provided.
    """

    results: List[date] = []
    year = start.year

    month_index = {
        m.lower(): i + 1 for i, m in enumerate(CALENDAR_2026.keys())
    }

    for month, days in CALENDAR_2026.items():
        month_num = month_index[month.lower()]

        for day, info in days.items():
            abhishekams = info.get("abhishekam", [])

            for event in abhishekams:
                if deity and deity.lower() not in event.lower():
                    continue

                try:
                    event_day = date(year, month_num, day)
                except ValueError:
                    continue

                if start <= event_day <= end:
                    results.append(event_day)

    results.sort()
    return results

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
                    
                )

        return raw_text


    except Exception as e:
        logger.error("RAG fallback failed", exc_info=True)
        return (
            "• That information is currently unavailable.\n\n"
            
        )
    
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
    SATYANARAYANA_POOJA = "SATYANARAYANA_POOJA"
    WEEKLY_ABHISHEKAM ="WEEKLY_ABHISHEKAM"
    ABHISHEKAM_SPONSORSHIP ="ABHISHEKAM_SPONSORSHIP"
    EVENTS = "EVENTS"
    KALYANAM = "KALYANAM"
    PANCHANG_TODAY = "PANCHANG_TODAY"
    PANCHANG_TOMORROW = "PANCHANG_TOMORROW"
    PANCHANG_DATE = "PANCHANG_DATE"
    LUNAR_DATES = "LUNAR_DATES"
    HOMAMS = "HOMAMS"
    HOMAM_ITEMS = "HOMAM_ITEMS"
    ARJITHA_SEVA = "ARJITHA_SEVA"
    VAHANA_POOJA = "VAHANA_POOJA"
    CONTACTS = "CONTACTS"
    COMMITTEE = "COMMITTEE"
    CULTURAL = "CULTURAL"
    RAG_FALLBACK = "RAG_FALLBACK"
    

INTENT_HANDLERS = {
    #story
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
    Intent.WEEKLY_ABHISHEKAM: [handle_abhishekam],
    Intent.ABHISHEKAM_SPONSORSHIP: [handle_abhishekam],

    #events
    Intent.EVENTS: [handle_calendar_events],

    #kalyanam
    Intent.KALYANAM: [handle_kalyanam],
    #satyanarayana
    Intent.SATYANARAYANA_POOJA: [handle_satyanarayana_pooja],

    #panchang
    Intent.PANCHANG_TODAY: [handle_panchang],
    Intent.PANCHANG_TOMORROW: [handle_panchang],
    Intent.PANCHANG_DATE: [handle_panchang],
    Intent.LUNAR_DATES: [handle_lunar_dates],

    #homams
    Intent.HOMAMS: [handle_homam],
    Intent.HOMAM_ITEMS: [handle_items_required],
    
    #arjithaseva
    Intent.ARJITHA_SEVA: [handle_arjitha_seva],
    Intent.VAHANA_POOJA: [handle_vahana_pooja],
    
    #templecontacts
    Intent.CONTACTS: [handle_contacts],
    Intent.COMMITTEE: [handle_committee_queries],
    Intent.CULTURAL: [handle_cultural_programs],
    
    #rag
    Intent.RAG_FALLBACK: [handle_rag_fallback],

}

def classify_intent(q: str) -> Intent:
    q = q.lower()

    # ---------------- VEDIC RECITATIONS (STRICT ESCALATION) ----------------
    if any(w in q for w in [
        "suktham", "sukthams",
        "sahasranamam", "sahasranama", "sahasranamams",
        "nama sankeerthanam", "namasankeerthanam",
        "vishnu sahasranamam", "lalitha sahasranamam",
        "recitation", "chanting", "parayanam",
        "naama sankeerthanam"
    ]):
        return Intent.VEDIC_RECITATION
    
    # ---------------- ITEMS / SAMAGRI (HIGH PRIORITY) ----------------
    if any(w in q for w in ["item", "items", "samagri", "materials", "bring", "required", "need"]):
        return Intent.HOMAM_ITEMS

    
    # ---------------- STORY / SIGNIFICANCE ----------------
    if any(w in q for w in [
        "story", "significance", "meaning", "why is", "why do we",
        "importance", "about", "legend"
    ]):
    # Avoid date queries like "when is", "dates"
        if not any(w in q for w in ["date", "dates", "when", "time", "timing"]):
            return Intent.STORY
        
    # ---------------- FESTIVALS (CALENDAR-DRIVEN) ----------------
    if any(w in q for w in [
        "festival", "festivals",
        "utsavam", "utsav", "celebration"
    ]):
        return Intent.EVENTS
    
    # ---------------- PANCHANG ----------------
    if any(w in q for w in ["panchang", "tithi", "nakshatra", "star","panchangam"]):
        if "tomorrow" in q:
            return Intent.PANCHANG_TOMORROW
        if any(m in q for m in [
            "jan","feb","mar","apr","may","jun",
            "jul","aug","sep","oct","nov","dec"
        ]) or any(c.isdigit() for c in q):
            return Intent.PANCHANG_DATE
        return Intent.PANCHANG_TODAY

    # ---------------- EVENTS (HIGH PRIORITY) ----------------    
    # Use EVENTS only when NO specific domain keyword exists
    
    if any(w in q for w in [
        "event", "events", "happening", "schedule", "program", 
    ]) and not any(w in q for w in [
        "panchang", "panchangam", "tithi", "nakshatra",
        "abhishekam", "homam", "kalyanam",
        "satyanarayana", "suprabhata", "pooja"
    ]):
        return Intent.EVENTS

      
    # ---------------- SATYANARAYANA POOJA (HIGH PRIORITY) ----------------
    if "satyanarayana" in q:
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
  
    # ---------------- LUNAR DATES (POORNIMA / AMAVASYA) ----------------
    if any(w in q for w in ["poornima", "purnima", "amavasya", "new moon", "full moon"]):
        return Intent.LUNAR_DATES

    
    
    # ---------------- HOMAMS ----------------
    if "homam" in q:
        return Intent.HOMAMS
    # ---------------- / KALYANAM ----------------
    if "kalyanam" in q:
        return Intent.KALYANAM

    # ---------------- ABHISHEKAM ----------------
    if "abhishekam" in q:

        # Sponsorship / amount queries
        if any(w in q for w in [
            "sponsor", "sponsorship", "amount", "cost", "price"
        ]):
            return Intent.ABHISHEKAM_SPONSORSHIP

        # Calendar / date-based queries
        if any(w in q for w in [
            "when", "date", "today", "next", "month", "this week", "next week"
        ]):
            return Intent.WEEKLY_ABHISHEKAM

        # Weekly schedule (Abhishekam-specific)
        if any(w in q for w in ["schedule", "weekly"]):
            return Intent.WEEKLY_ABHISHEKAM

        return Intent.WEEKLY_ABHISHEKAM

    if any(p in q for p in ["next week", "coming week", "upcoming week", "following week"]):
        return Intent.EVENTS

    if "suprabhata" in q:
        return Intent.DAILY_POOJA
    
    if "daily pooja" in q:
        return Intent.DAILY_POOJA
    
    # ---------------- ARJITHA ----------------
    if "arjitha" in q:
        return Intent.ARJITHA_SEVA

    # ---------------- VAHANA ----------------
    if any(w in q for w in ["vahana", "vehicle", "car pooja"]):
        return Intent.VAHANA_POOJA

    # ---------------- SUPRABHATA SEVA ----------------
    if "suprabhata" in q:
        return Intent.DAILY_POOJA

    # ---------------- CONTACTS (PEOPLE) ----------------
    if any(w in q for w in [
        "chairman", "president", "manager",
        "secretary", "treasurer", "phone", "email", "contact"
    ]):
        return Intent.CONTACTS

    # ---------------- COMMITTEES ----------------
    if any(w in q for w in [
        "committee", "committees", "board",
        "trustee", "leadership", "executive committee"
    ]):
        return Intent.COMMITTEE

    # ---------------- CULTURAL ----------------
    if any(w in q for w in ["dance", "music", "bhajan", "concert", "cultural"]):
        return Intent.CULTURAL

    return Intent.RAG_FALLBACK
      
def answer_user(
    query: str,
    user_id: Optional[str] = None,
    message_ts: Optional[int] = None
):
    # --------------------------------------------------
    # Resolve current time
    # --------------------------------------------------
    if message_ts:
        now = datetime.fromtimestamp(message_ts, ZoneInfo("America/Denver"))
    else:
        now = datetime.now(ZoneInfo("America/Denver"))

    if not query or not isinstance(query, str):
        return "Please provide a valid question."

    # --------------------------------------------------
    # Normalize query
    # --------------------------------------------------
    query = query.strip()[:MAX_QUERY_LEN]
    
    q = normalize_query(query) 
    q = autocorrect_query(q)
    q = normalize_intent(q)
  
    logger.info("AFTER NORMALIZATION: %s", q)


    intent = classify_intent(q)
    logger.info("Intent=%s | Query=%s", intent.value, q)

        # ==================================================
    # 📆 MONTHLY EVENTS / POOJA SCHEDULE
    # ==================================================
    if intent == Intent.EVENTS and any(w in q for w in [
    "monthly", "month", "this month", "next month",
    "january", "february", "march", "april",
    "may", "june", "july", "august",
    "september", "october", "november", "december"
]):


        sections: List[str] = []

        # -------- Resolve target month --------
        month_map = {
            "january": 1, "february": 2, "march": 3, "april": 4,
            "may": 5, "june": 6, "july": 7, "august": 8,
            "september": 9, "october": 10, "november": 11, "december": 12
        }

        target_month = now.month
        target_year = now.year
        # Default: "monthly" → current month
        if "monthly" in q or "month" in q:
            target_month = now.month
            target_year = now.year


        for name, num in month_map.items():
            if name in q:
                target_month = num
                break

        if "next month" in q:
            temp = now.replace(day=1) + timedelta(days=32)
            target_month = temp.month
            target_year = temp.year

        month_name = datetime(target_year, target_month, 1).strftime("%B").lower()

        sections.append(
            f"📅 EVENTS – {month_name.capitalize()} {target_year}"
        )

        # -------- Calendar lookup --------
        month_data = {}
        if target_year == 2026:
            month_data = CALENDAR_2026.get(month_name, {})

        found = False

        for day in sorted(month_data.keys()):
            info = month_data[day]
            for key in ["festival", "abhishekam", "homam", "kalyanam"]:
                for event in info.get(key, []):
                    found = True
                    sections.append(
                        f"• {day} {month_name.capitalize()}: {event}"
                    )

        if found:
            return finalize("\n".join(sections), q)

        return finalize(
            f"• No special poojas or events are listed for {month_name.capitalize()} {target_year}.",
            q
        )

    # ==================================================
    # ⭐ TODAY / NOW / WHAT'S HAPPENING (COMPOSITE VIEW)
    # ==================================================
    if intent == Intent.EVENTS and any(w in q for w in [
    "today", "now", "what's happening", "whats happening"
]):
        sections: List[str] = []
        sections.append(
        f"📅 Date: {now.strftime('%B %d, %Y')} ({now.strftime('%A')})"
)


        # --------------------------------------------------
        # 1️⃣ DAILY POOJA (NO STATUS WORDS)
        # --------------------------------------------------
        daily = handle_daily_pooja("daily pooja", now)
        if daily:
            sections.append(daily)

        # --------------------------------------------------
        # 2️⃣ CALENDAR EVENTS (SOURCE OF TRUTH)
        # --------------------------------------------------
        today = now.date()
        cal_lines = ["📅 EVENTS – TODAY", ""]

        day_info = {}
        if now.year == 2026:
            month = today.strftime("%B").lower()
            day_info = CALENDAR_2026.get(month, {}).get(today.day, {})

        found_calendar_event = False

        for key in ["festival", "abhishekam", "homam", "kalyanam"]:
            for item in day_info.get(key, []):
                found_calendar_event = True
                cal_lines.append(f"• {item}")

        if found_calendar_event:
            sections.append("\n".join(cal_lines))

        # --------------------------------------------------
        # 3️⃣ PANCHANGAM (FORCED TODAY)
        # --------------------------------------------------
        panchang_today = handle_panchang("panchang today", now)
        if panchang_today:
            sections.append(panchang_today)

        # --------------------------------------------------
        # FINAL RESPONSE
        # --------------------------------------------------
        if sections:
            return finalize("\n\n".join(sections), q)

        return finalize(
            "• No special poojas or events are scheduled for today.",
            q
        )
    # ==================================================
    # 🔁 STANDARD HANDLER FLOW
    # ==================================================
    handlers = INTENT_HANDLERS.get(intent, [])
    logger.info("Handlers=%s", handlers)
    print("QUERY:", q)
    tokens = set(q.split())

    ESCALATION_TOKENS = {
        "manager", "office", "contact",
        "phone", "number",
        "priest", "archaka", "pandit", "pujari"
    }

    if tokens & ESCALATION_TOKENS:
        return finalize(
            "• Please contact the Temple office for assistance from the Priest or Temple Manager.",
            q
        )
    
    for handler in handlers:
        try:
            result = handler(q, now)
            if result:
                print("result", result)
                return finalize(result, q)
        except Exception:
            logger.error(f"Handler {handler.__name__} failed", exc_info=True)

    # ==================================================
    # ☎️ CONDITIONAL ESCALATION (LAST RESORT)
    # ==================================================
    
    

    # --------------------------------------------------
    # Fallback
    # --------------------------------------------------
    return finalize(
        "• I don’t have specific information on that right now.",
        q
    )





        


