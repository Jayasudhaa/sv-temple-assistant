# backend/ask_temple.py
import os, json, re, boto3
from datetime import datetime
from zoneinfo import ZoneInfo
from .retrieval import get_chunks

# =============================================================
# 1) INTENT DETECTION — identifies what user wants
# =============================================================
def detect_intent(q: str) -> str:
    q = (q or "").lower()

    if any(w in q for w in ["panchang", "panchanga", "tithi", "nakshatra"]):
        return "panchangam"

    if any(w in q for w in ["when is", "date", "which day", "next", "schedule"]):
        return "date"

    if any(w in q for w in ["items", "list", "materials", "what do i need"]):
        return "items"

    if any(w in q for w in ["meaning", "why", "significance"]):
        return "meaning"

    if any(w in q for w in ["timings", "hours", "open", "close"]):
        return "timings"

    return "general"


# =============================================================
# 2) MONTH HELPERS FOR PANCHANGAM (restored)
# =============================================================
_MONTHS = {
    "january":"jan","february":"feb","march":"mar","april":"apr","may":"may","june":"jun",
    "july":"jul","august":"aug","september":"sep","october":"oct","november":"nov","december":"dec"
}

def _target_month(q: str, now: datetime) -> str:
    """Find which month user is asking about. Default = current month."""
    ql = (q or "").lower()
    for full, short in _MONTHS.items():
        if full in ql or f"{short} " in ql:
            return full
    return now.strftime("%B").lower()

def _prefer_month(chunks, month_lower: str):
    """Prioritize chunks matching that month."""
    key3 = _MONTHS[month_lower]
    pri, rest = [], []
    for c in chunks:
        src = (c.get("source") or "").lower()
        txt = (c.get("text") or "").lower()
        if month_lower in src or key3 in src or month_lower in txt:
            pri.append(c)
        else:
            rest.append(c)
    return pri + rest

def _dedupe_lines(lines):
    seen, out = set(), []
    for ln in lines:
        s = ln.strip()
        if s and s not in seen:
            seen.add(s)
            out.append(s)
    return out


# =============================================================
# 3) REMOVE THINKING TAGS (safety)
# =============================================================
_THINK_REGEXES = [
    r"(?is)<think>.*?</think>",
    r"(?is)```(?:thinking|reasoning|thoughts).*?```",
]

def _sanitize(text: str) -> str:
    if not isinstance(text, str): text = str(text)
    for pat in _THINK_REGEXES:
        text = re.sub(pat, "", text, flags=re.DOTALL | re.IGNORECASE)
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    return "\n".join(lines)


# =============================================================
# 4) TEMPLATE RESPONSES (fixed)
# =============================================================
def template_timings(ts):
    return f"""{ts}
Om Namo Venkateshaya Namah

• Temple is open 9:00 AM – 8:30 PM (Weekdays)  
• Weekends: 8:30 AM – 8:30 PM  
• Daily pooja typically at 9 AM & 10 AM  

For latest, visit https://svtempleco.org
Thank you. Om Namo Venkateshaya!
"""

def template_no_info(ts):
    return f"""{ts}
Om Namo Venkateshaya Namah
- I do not have information yet.
Thank you. Om Namo Venkateshaya!"""


# =============================================================
# 5) PANCHANGAM EXTRACTOR (restored + improved)
# =============================================================
def extract_panchangam(chunks, month_lower, ts):
    """Extract only: Tithi, Nakshatra, Event lines."""
    lines = []

    prioritized = _prefer_month(chunks, month_lower)

    for c in prioritized[:8]:
        for ln in c.get("text","").splitlines():
            l = ln.lower()
            if "tithi:" in l or "nakshatra:" in l or "event:" in l:
                lines.append("• " + ln.strip())

    lines = _dedupe_lines(lines)

    if not lines:
        return None

    body = "\n".join(lines[:20])
    return f"""{ts}
Om Namo Venkateshaya Namah
{body}

Thank you. Om Namo Venkateshaya!
"""


# =============================================================
# 6) LLM ANSWER (only for meaning/general)
# =============================================================
def llm_answer(context, question):
    prompt = f"""
You are the official SV Temple Colorado assistant.
Answer clearly in 3–5 short lines.
Do not include Panchangam or long pooja lists unless asked.

Context:
{context}

User question: {question}

Give a short devotional answer.
"""

    client = boto3.client("bedrock-runtime")
    resp = client.invoke_model(
        modelId=os.getenv("LLM_MODEL_ID", "deepseek-chat"),
        body=json.dumps({"prompt": prompt, "max_tokens": 150, "temperature": 0.2}),
        contentType="application/json",
    )

    body = resp["body"].read()
    try:
        out = json.loads(body)
        text = out.get("outputText") or out.get("content") or ""
    except:
        text = body.decode("utf-8","ignore")

    return _sanitize(text)


# =============================================================
# 7) MAIN LOGIC — decides answer based on intent
# =============================================================
def answer_user(question: str) -> str:
    now = datetime.now(ZoneInfo("America/Denver"))
    ts = now.strftime("%B %d, %Y %I:%M %p %Z")

    intent = detect_intent(question)

    # Retrieve RAG context
    chunks = get_chunks(question, k=10)
    month_lower = _target_month(question, now)
    context = "\n".join(c.get("text","") for c in chunks)

    # --------------------
    # A) PANCHANGAM ANSWER
    # --------------------
    if intent == "panchangam":
        p = extract_panchangam(chunks, month_lower, ts)
        if p:
            return p
        return template_no_info(ts)

    # --------------------
    # B) TEMPLE TIMINGS
    # --------------------
    if intent == "timings":
        return template_timings(ts)

    # --------------------
    # C) ITEMS LIST
    # --------------------
    if intent == "items":
        items = []
        for c in chunks:
            for ln in c.get("text","").splitlines():
                if any(x in ln.lower() for x in ["nos", "lb", "packet", "piece", "box"]):
                    items.append("• " + ln.strip())

        if not items:
            return template_no_info(ts)

        return f"""{ts}
Om Namo Venkateshaya Namah
Satyanarayana Swamy Pooja Items:
{chr(10).join(items[:20])}

Thank you. Om Namo Venkateshaya!
"""

    # --------------------
    # D) DATE QUESTIONS
    # --------------------
    if intent == "date":
        for c in chunks:
            for ln in c.get("text","").splitlines():
                if any(x in ln.lower() for x in ["event:", "pooja", "abhishekam"]):
                    return f"""{ts}
Om Namo Venkateshaya Namah

• {ln.strip()}
• Please visit https://svtempleco.org for updates.

Thank you. Om Namo Venkateshaya!
"""
        return template_no_info(ts)

    # --------------------
    # E) MEANING / GENERAL
    # --------------------
    ans = llm_answer(context, question).strip()
    if not ans:
        return template_no_info(ts)

    return f"""{ts}
Om Namo Venkateshaya Namah
{ans}

Thank you. Om Namo Venkateshaya!
"""
