<<<<<<< HEAD
# backend/ask_temple.py

import os
import json
import boto3
from retrieval import retrieve_chunks

BASE_DIR = os.path.dirname(__file__)
CONFIG_DIR = os.path.join(BASE_DIR, "..", "config")

SYSTEM_PROMPT_PATH = os.path.join(CONFIG_DIR, "system_prompt.txt")
STATUS_PATH = os.path.join(CONFIG_DIR, "temple_status.json")

BEDROCK_REGION = "us-east-1"
LLM_MODEL_ID = "anthropic.claude-3-haiku-20240307-v1:0"  # example fast/cheap model in Bedrock

bedrock_runtime = boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)

def load_system_prompt():
    with open(SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read()

def load_status():
    with open(STATUS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def build_user_prompt(status_info: dict, chunks: list[dict], user_question: str) -> str:
    """
    Create one big prompt string for the model.
    We include:
    - Temple status (open/closed)
    - Retrieved context chunks
    - User's actual question
    - Instructions
    """
    status_block = (
        "TEMPLE STATUS:\n"
        f"{status_info.get('message','')}\n"
        f"Next: {status_info.get('next_open_time','')}\n\n"
    )

    context_block_lines = []
    for c in chunks:
        context_block_lines.append(
            f"[Source: {c['source']}]\n{c['text']}\n"
        )
    context_block = "\n".join(context_block_lines)

    instructions = (
        "Answer ONLY using Temple Status and Context above. "
        "If the answer is not found, say: "
        "\"Please contact a temple volunteer for this request.\" "
        "Never invent times, phone numbers, or prices."
    )

    user_block = (
        status_block +
        "CONTEXT FROM TEMPLE DOCUMENTS:\n" +
        context_block +
        "\nUSER QUESTION:\n" +
        user_question +
        "\n\n" +
        "INSTRUCTIONS:\n" +
        instructions
    )

    return user_block

def call_bedrock_chat(system_prompt: str, user_prompt: str) -> str:
    """
    Call Bedrock chat model (Anthropic Claude style).
    Different models have slightly different request/response schema.
    We'll build Anthropic-style body that Bedrock expects.
    """
    body = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": 300,
        "temperature": 0.2
    }

    response = bedrock_runtime.invoke_model(
        modelId=LLM_MODEL_ID,
        body=json.dumps(body)
    )

    resp_body = json.loads(response["body"].read())

    # For Claude models in Bedrock, response["body"] usually decodes to a dict
    # whose text output is in something like resp_body["output"][0]["content"][0]["text"].
    # We'll code defensively:
    try:
        answer_text = resp_body["output"][0]["content"][0]["text"]
    except Exception:
        # fallback if Bedrock model returns in a different field
        answer_text = json.dumps(resp_body)

    return answer_text.strip()

def answer_user(question_text: str) -> str:
    """
    Public function you'll call from Lambda.
    """
    status_info = load_status()
    system_prompt = load_system_prompt()

    # get top chunks from FAISS
    chunks = retrieve_chunks(question_text, k=4)

    # build the user message for the LLM
    user_prompt = build_user_prompt(status_info, chunks, question_text)

    # ask the model
    llm_answer = call_bedrock_chat(system_prompt, user_prompt)

    if not llm_answer.strip():
        return "Please contact a temple volunteer for this request."

    return llm_answer
=======
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
import calendar
import re

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
from backend.get_timing import handle_calendar_events,handle_abhishekam
from backend.kalyanam_queries import handle_kalyanam
from backend.food_query import FOOD_KEYWORDS
from backend.constants import MONTHLY_SCHEDULE

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

    # -------- TODAY --------
    "today",
    "today's",
    "todays",
    "today schedule",
    "today events",
    "today at temple",

    # -------- TOMORROW --------
    "tomorrow",
    "tomorrow's",
    "tomorrows",
    "tomorrow schedule",
    "tomorrow events",
    "tomo",
    "tomo's events",
    "tomo's activities",

    # -------- YESTERDAY --------
    "yesterday",
    "yesterday's",
    "yesterdays",

    # -------- WEEK --------
    "this week",
    "next week",
    "last week",
    "coming week",
    "upcoming week",
    "following week",
    "current week",
    "weekend",
    "weekends",
    "next weekend",

    "upcoming",
    "coming",
    "upcoming events",
    "upcoming activities",

    # -------- MONTH --------
    "this month",
    "next month",
    "last month",
    "upcoming month",
    "current month",

    # -------- YEAR --------
    "this year",
    "next year",
    "last year",
]

calendar_words = [

    # -------- EVENTS --------
    "event",
    "events",
    "festival",
    "festivals",

    # -------- SCHEDULE --------
    "schedule",
    "timings",
    "timing",
    "time",
    "program",
    "programs",
    "activity",
    "activities",

    # -------- HAPPENING --------
    "happening",
    "whats happening",
    "what's happening",
    "what is happening",
    "what all is happening",

    # -------- SPECIAL --------
    "special",
    "special events",
    "today's special",
    "todays special",

    # -------- GENERIC USER PHRASES --------
    "what's going on",
    "whats going on",
    "what is going on",
    "anything today",
    "anything special",
    "anything happening",
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
    q = normalize_query(q.lower())

    # ==================================================
    # 🔱 VEDIC RECITATIONS (STRICT)
    # ==================================================
    if any(w in q for w in [
        "suktham", "sukthams",
        "sahasranamam", "sahasranama", "sahasranamams",
        "vishnu sahasranamam", "lalitha sahasranamam",
        "nama sankeerthanam", "namasankeerthanam",
        "naama sankeerthanam",
        "recitation", "chanting", "parayanam"
    ]):
        return Intent.VEDIC_RECITATION

    # ==================================================
    # 🧺 ITEMS / SAMAGRI (HIGH PRIORITY)
    # ==================================================
    if any(w in q for w in [
        "item", "items", "samagri", "materials",
        "bring", "required", "need"
    ]):
        return Intent.HOMAM_ITEMS
    
     # ==================================================
    # 🚗 VAHANA POOJA
    # ==================================================
    if any(w in q for w in ["vahana", "vehicle", "car pooja"]):
        return Intent.VAHANA_POOJA

    # ==================================================
    # 📞 CONTACTS
    # ==================================================
    if any(w in q for w in [
        "chairman", "president", "manager", "temple manager",
        "secretary", "treasurer",
        "phone", "email", "contact"
    ]):
        return Intent.CONTACTS

    # ==================================================
    # 👥 COMMITTEES
    # ==================================================
    if any(w in q for w in [
        "committee", "committees", "board",
        "trustee", "leadership", "executive committee"
    ]):
        return Intent.COMMITTEE

    # ==================================================
    # 🎶 CULTURAL
    # ==================================================
    if any(w in q for w in ["dance", "music", "bhajan", "concert", "cultural", "singing", "cultural programs","cultural programme"]):
        return Intent.CULTURAL


    # ==================================================
    # 📖 STORY / SIGNIFICANCE (NO DATE WORDS)
    # ==================================================
    if any(w in q for w in [
        "story", "significance", "meaning",
        "importance", "legend", "about", "why"
    ]) and not any(w in q for w in [
        "date", "dates", "when", "time", "timing"
    ]) and not any(w in q for w in [
        "kalyanam",
        "abhishekam",
        "homam",
        "pooja",
        "seva"]):
        return Intent.STORY

    # ==================================================
    # 🪐 PANCHANG (DATE-SENSITIVE)
    # ==================================================
    if any(w in q for w in ["panchang", "panchangam", "tithi", "nakshatra", "star"]):
        if "tomorrow" in q:
            return Intent.PANCHANG_TOMORROW
        if any(c.isdigit() for c in q) or any(m in q for m in [
            "jan","feb","mar","apr","may","jun",
            "jul","aug","sep","oct","nov","dec"
        ]):
            return Intent.PANCHANG_DATE
        return Intent.PANCHANG_TODAY

    # ==================================================
    # 🍽️ FOOD / ANNADANAM
    # ==================================================
    if any(w in q for w in ["annadanam", "cafeteria", "food", "lunch", "prasadam", "annadanam today"]):
        return Intent.FOOD
      # ---------------- SATYANARAYANA POOJA (HIGH PRIORITY) ----------------
    if "satyanarayana" in q or "satya narayana" in q:
        return Intent.SATYANARAYANA_POOJA

    # ==================================================
    # 🕰️ TEMPLE HOURS
    # ==================================================
    if any(w in q for w in ["open", "close", "hours", "timing"]) \
    and "satyanarayana" not in q \
    and "satya narayana" not in q:
        return Intent.TEMPLE_HOURS

    # ==================================================
    # 📍 LOCATION
    # ==================================================
    if any(w in q for w in ["address", "location", "where is", "directions"]):
        return Intent.LOCATION

    # ==================================================
    # 🌕 LUNAR DATES (POORNIMA / AMAVASYA)
    # ==================================================
    if any(w in q for w in [
        "poornima", "purnima", "amavasya",
        "new moon", "full moon"
    ]):
        return Intent.LUNAR_DATES

    # ==================================================
    # 🔥 HOMAMS
    # ==================================================
    if "homam" in q:
        return Intent.HOMAMS

    # ==================================================
    # 💍 KALYANAM
    # ==================================================
    if "kalyanam" in q:
        return Intent.KALYANAM

    # ==================================================
    # 🪔 ABHISHEKAM
    # ==================================================
    if "abhishekam" in q:
        if any(w in q for w in [
            "sponsor", "sponsorship", "amount", "cost", "price"
        ]):
            return Intent.ABHISHEKAM_SPONSORSHIP
        return Intent.WEEKLY_ABHISHEKAM

    # ==================================================
    # 📅 EVENTS (GENERIC — TIME RESOLVED LATER)
    # ==================================================
    if (
    (
        any(t in q for t in time_words)
        or any(m.lower() in q for m in calendar.month_name if m)
        or any(w in q for w in calendar_words)
    )
    and not any(f in q for f in FOOD_KEYWORDS)
    and not any(w in q for w in [
        "daily pooja",
        "suprabhata",
        "nitya archana",
        "archana",
    ])
):
        return Intent.EVENTS

    # ==================================================
    # 🌅 DAILY POOJA / SUPRABHATA
    # ==================================================
    if "suprabhata" in q or "daily pooja" in q:
        return Intent.DAILY_POOJA

    # ==================================================
    # 🪔 ARJITHA SEVA
    # ==================================================
    if "arjitha" in q:
        return Intent.ARJITHA_SEVA

    # ==================================================
    # 🤖 FALLBACK (RAG)
    # ==================================================
    return Intent.RAG_FALLBACK

def is_weekend_day(dt: datetime) -> bool:
    return dt.weekday() >= 5   # 5 = Saturday, 6 = Sunday

def ensure_event_time(q: str) -> str:
    # Do NOT force today if month/year is already specified
    if any(m.lower() in q for m in calendar.month_name if m):
        return q
    if re.search(r"\b20\d{2}\b", q):
        return q
    if any(t in q for t in time_words):
        return q
    return q + " today"

def answer_user(
    query: str,
    user_id: Optional[str] = None,
    message_ts: Optional[int] = None
):
    # ------------------ TIME ------------------
    now = (
        datetime.fromtimestamp(message_ts, ZoneInfo("America/Denver"))
        if message_ts else
        datetime.now(ZoneInfo("America/Denver"))
    )

    if not query or not isinstance(query, str):
        return "Please provide a valid question."

    # ------------------ NORMALIZATION ------------------
    q = normalize_query(query.strip()[:MAX_QUERY_LEN])
    q = autocorrect_query(q)
    q = normalize_intent(q)
   

    print("after normalization",q)
    print("[DEBUG-NORM]", q)

    intent = classify_intent(q)   # ✅ FIRST classify
    if intent == Intent.EVENTS and not any(
    m.lower() in q for m in calendar.month_name if m
):
        q = ensure_event_time(q)

    print(f"[DEBUG] INTENT={intent.name} | QUERY='{q}' | NOW={now.date()}")

    # ------------------ ESCALATION ------------------
    if set(q.split()) & {
        "priest", "archaka", "pandit", "pujari","kanakabhishekam"
    }:
        return finalize(
            "• Please contact the Temple office for assistance from the Priest or Temple Manager.",
            q
        )
    # ==================================================
    # 🪔 HOW TO BOOK POOJA / SEVA (EXPLICIT ONLY)
    # ==================================================
    if any(k in q for k in [
        "how to book",
        "how do i book",
        "how to schedule",
        "how do i schedule",
        "book pooja",
        "schedule pooja",
        "book puja",
        "schedule puja",
    ]):
        return finalize(
            "🪔 HOW TO BOOK A POOJA / SEVA\n\n"
            "• Decide the pooja or seva type\n"
            "• Choose temple or home service\n"
            "• Contact the temple office to confirm date & priest availability\n"
            "• Complete sponsorship/payment as applicable\n\n"
            "📞 Temple office can assist with scheduling and guidance.",
            q
        )

    # ------------------ EVENT HANDLING (SINGLE ENTRY) ------------------
    result = handle_calendar_events(q, now)

    if intent == Intent.EVENTS:
        result = handle_calendar_events(q, now)
        print("result", result)

        if not result:
            return finalize(
                "• No special events scheduled.",
                q
            )

        # ---------- TODAY ----------
        if "📅 EVENTS – TODAY" in result and "today" in q:

            blocks = [result]

            daily = handle_daily_pooja("daily pooja", now)
            if daily:
                blocks.append(daily)

            panchang = handle_panchang("panchang today", now)
            if panchang:
                blocks.append(panchang)

            if not is_weekend_day(now):
                blocks.append(
                    "🍽️ ANNADANAM\n"
                    f"• No Annadanam today ({now.strftime('%A')})\n"
                    "• Served on Saturdays & Sundays only"
                )

            return finalize("\n\n".join(blocks), q)

        # ---------- TOMORROW ----------
        if "📅 EVENTS – TOMORROW" in result and "tomorrow" in q:
            blocks = [result]

            # 1️⃣ Tomorrow Panchang (reuse existing logic)
            panchang = handle_panchang("panchang tomorrow", now)
            if panchang:
                blocks.append(panchang)

            # Reuse existing temple hours logic
            tomorrow_now = now + timedelta(days=1)
            hours = handle_temple_hours("temple hours", tomorrow_now)

            if hours:
                blocks.append(hours)

            if not is_weekend_day(tomorrow_now):
                blocks.append(
                    "🍽️ ANNADANAM\n"
                    f"• No Annadanam tomorrow ({tomorrow_now.strftime('%A')})\n"
                    "• Served on Saturdays & Sundays only"
                )


            return finalize("\n\n".join(blocks), q)
            

    # -------- WEEK / MONTH / OTHER --------
        if any(m.lower() in q for m in calendar.month_name if m) or "month" in q:
            return finalize(result, q)
   
    # ------------------ MONTHLY SCHEDULE (COMPOSED VIEW) ------------------
    if (
        intent == Intent.EVENTS
        and "month" in q
        and any(w in q for w in ["schedule", "pooja", "events"])
    ):
        blocks = []
        blocks.append("📆 MONTHLY POOJA SCHEDULE")
        blocks.append("")
        blocks.extend(MONTHLY_SCHEDULE)

        # 1️⃣ Monthly calendar events
        cal = handle_calendar_events(q, now)
        if cal:
            blocks.append(cal)

        # 2️⃣ Monthly Abhishekam schedule
        abhi = handle_abhishekam(f"abhishekam {q}", now)
        if abhi:
            blocks.append(abhi)

        # 3️⃣ Monthly Kalyanam (optional, safe)
        kaly = handle_kalyanam(f"kalyanam {q}", now)
        if kaly:
            blocks.append(kaly)

        return finalize("\n\n".join(blocks), q)


    # ------------------ STANDARD HANDLERS ------------------
    for handler in INTENT_HANDLERS.get(intent, []):
        try:
            result = handler(q, now)
            if result:
                return finalize(result, q)
        except Exception:
            logger.error(f"Handler {handler.__name__} failed", exc_info=True)

    return finalize(
        "• I don’t have specific information on that right now.",
        q
    )


>>>>>>> dev
