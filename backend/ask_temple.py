# backend/ask_temple.py
import os, json, re, boto3
from datetime import datetime
from zoneinfo import ZoneInfo
from .retrieval import get_chunks

# ---------------- NEW: month helpers + dedupe ----------------
_MONTHS = {
    "january":"jan","february":"feb","march":"mar","april":"apr","may":"may","june":"jun",
    "july":"jul","august":"aug","september":"sep","october":"oct","november":"nov","december":"dec"
}
def _target_month(q: str, now: datetime) -> str:
    ql = (q or "").lower()
    for full, short in _MONTHS.items():
        if full in ql or f"{short} " in ql:
            return full
    return now.strftime("%B").lower()

def _prefer_month(chunks, month_lower: str):
    key3 = _MONTHS[month_lower]  # e.g., "nov"
    pri = []
    rest = []
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
            seen.add(s); out.append(s)
    return out
# -------------------------------------------------------------

_THINK_REGEXES = [
    r"(?is)<think>.*?</think>", r"(?is)```(?:thinking|reasoning|thoughts).*?```",
    r"(?is)\[BEGIN(?: REASONING| THINKING).*?\[END(?: REASONING| THINKING)\]",
    r"(?is)^\s*(?:Okay, let's see\.|Reasoning:|Thoughts?:).*$",
]

def _extract_text_from_bedrock(resp) -> str:
    body = resp["body"].read()
    try:
        data = json.loads(body)
    except Exception:
        return body.decode("utf-8","ignore")
    if isinstance(data, dict) and "choices" in data and data["choices"]:
        ch = data["choices"][0]
        if isinstance(ch, dict) and "text" in ch: return ch["text"]
        msg = ch.get("message") or {}
        if isinstance(msg, dict):
            if isinstance(msg.get("content"), str): return msg["content"]
            if isinstance(msg.get("content"), list):
                parts = [p["text"] for p in msg["content"] if isinstance(p,dict) and "text" in p]
                if parts: return "\n".join(parts)
    if isinstance(data, dict) and "outputText" in data: return data["outputText"]
    if isinstance(data, dict) and "content" in data and isinstance(data["content"], list):
        parts = [p.get("text","") for p in data["content"] if isinstance(p,dict)]
        return "\n".join([p for p in parts if p])
    if isinstance(data, dict) and "completions" in data and data["completions"]:
        comp = data["completions"][0]
        return comp.get("data",{}).get("text","") or comp.get("completion","")
    return json.dumps(data, ensure_ascii=False)

def _sanitize(text: str) -> str:
    if not isinstance(text, str): text = str(text)
    for pat in _THINK_REGEXES:
        text = re.sub(pat,"",text, flags=re.DOTALL|re.IGNORECASE)
    opener = "Om Namo Venkateshaya Namah"
    if opener in text:
        text = opener + "\n" + text.split(opener,1)[1].strip()
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    bullets = [ln for ln in lines if ln.startswith(("•","-"))]
    return "\n".join(bullets) if bullets else "\n".join(lines).strip()

def _format_no_context(ts: str) -> str:
    return f"""{ts}
- No special events today.
- Daily pooja at 9:00 AM & 10:00 AM
- Please call 303-660-9555.

Thank you. Om Namo Narayanaya!"""

# ---------------- NEW: deterministic panchang extractor ----------------
def _try_panchang_answer(chunks, month_lower: str, ts: str):
    want = {"tithi","nakshatra","panchang","panchanga"}
    # collect lines containing Tithi/Nakshatra/Event from that month’s chunks
    lines = []
    for c in _prefer_month(chunks, month_lower)[:8]:
        txt = c.get("text","")
        for ln in txt.splitlines():
            lnl = ln.lower()
            if ("tithi:" in lnl or "nakshatra:" in lnl or "event:" in lnl):
                lines.append("• " + ln.strip())
    lines = _dedupe_lines(lines)
    if lines:
        body = "\n".join(lines[:20])
        return f"""{ts}
Om Namo Venkateshaya Namah
{body}

Thank you. Om Namo Venkateshaya!"""
    return None
# -----------------------------------------------------------------------

def answer_user(question: str) -> str:
    now = datetime.now(ZoneInfo("America/Denver"))
    ts = now.strftime("%B %d, %Y %I:%M %p %Z")

    # 1) retrieve more, then re-rank for the month in question
    chunks = get_chunks(question, k=10)
    month_lower = _target_month(question, now)
    chunks = _prefer_month(chunks, month_lower)

    # 2) If the user asked panchang/tithi/nakshatra, return deterministic lines (no LLM)
    if any(w in (question or "").lower() for w in ["panchang","panchanga","tithi","nakshatra"]):
        maybe = _try_panchang_answer(chunks, month_lower, ts)
        if maybe: return maybe

    # 3) Otherwise, LLM answer (constrained to that month)
    context = "\n\n".join(c.get("text","") for c in chunks[:3])
    if not context.strip():
        return _format_no_context(ts)

    prompt = (
        "You are a warm, devotional assistant at Sri Venkateswara Swamy Temple of Colorado.\n"
        "Always start reply by saying \"Om Namo Venkateshaya Namah\".\n"
        "Answer ONLY in BULLET POINTS using exact words from the context.\n"
        f"Only answer for {month_lower.title()} of the given year; ignore any other months.\n"
        "Do not include any meta commentary, prefaces, <think> tags, or reasoning.\n"
        "If nothing matches, reply exactly: \"- I do not have information yet.\"\n\n"
        f"Context:\n{context}\n\nAnswer:"
    )

    try:
        client = boto3.client("bedrock-runtime")
        resp = client.invoke_model(
            modelId=os.getenv("LLM_MODEL_ID", "deepseek-chat"),
            body=json.dumps({"prompt": prompt, "max_tokens": 500, "temperature": 0.2}),
            contentType="application/json",
        )
        raw = _extract_text_from_bedrock(resp).strip()
        ans = _sanitize(raw) or "- I do not have information yet."
    except Exception:
        ans = "- I do not have information yet."

    if not ans.lstrip().startswith(("-", "•")):
        ans = "- " + ans.replace("\n", "\n- ")

    return f"""{ts}
Om Namo Venkateshaya Namah
{ans}

Thank you. Om Namo Venkateshaya!"""
