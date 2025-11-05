# app.py
import json, os, urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo
from backend.ask_temple import answer_user

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "svt-verify-123")
TOKEN        = os.getenv("WHATSAPP_ACCESS_TOKEN")
PHONE_ID     = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

now = datetime.now(ZoneInfo("America/Denver"))
current_month = now.strftime("%B")

def send_reply(to, text):
    url = f"https://graph.facebook.com/v22.0/{PHONE_ID}/messages"
    payload = {"messaging_product":"whatsapp","to":to,"type":"text","text":{"body":text[:1400]}}
    req = urllib.request.Request(url, json.dumps(payload).encode(), method="POST")
    req.add_header("Authorization", f"Bearer {TOKEN}")
    req.add_header("Content-Type", "application/json")
    try: urllib.request.urlopen(req, timeout=10)
    except: pass

# --- NEW: simple line-level de-duplication (keeps first occurrence) ---
def dedupe_bullets(text: str) -> str:
    out, seen = [], set()
    for line in text.splitlines():
        raw = line.rstrip()
        norm = raw.lstrip("-•").strip().lower()
        norm = " ".join(norm.split())
        if norm and norm not in seen:
            out.append(raw)
            seen.add(norm)
    return "\n".join(out)

def handler(event, context):
    if event.get("httpMethod") == "GET":
        qs = event.get("queryStringParameters", {})
        if qs.get("hub.mode") == "subscribe" and qs.get("hub.verify_token") == VERIFY_TOKEN:
            return {"statusCode":200, "body":qs.get("hub.challenge")}
        return {"statusCode":403}

    body = json.loads(event.get("body","{}"))
    for entry in body.get("entry",[]):
        for change in entry.get("changes",[]):
            msg = change.get("value",{}).get("messages",[{}])[0]
            if not msg.get("text"): continue
            user_text = msg["text"]["body"].strip().lower()

            if any(w in user_text for w in ["thank","thanks", "bye","Have a good day"]):
                send_reply(msg["from"], "You’re welcome! Blessings always.\nOm Namo Venkateshaya! Visit https://svtempleco.org/")
                return {"statusCode":200}

            if any(g in user_text for g in ["hello","hi","namaste"]):
                # Clean welcome greeting — no "homam cost"
                greeting = f""""SV Temple Castle Rock, Colorado, OM Namo Venkateshaya"
                               
{now:%A, %B %d, %Y}
{now:%I:%M %p MST}
{"─" * 30}

Welcome! How may I serve you?
Ask me anything
• {current_month} Events
• When is Satyanarayana Pooja?
• List of Homams?
• Daily Pooja Schedule
• Temple Timings
• Meaning of Hindu Rituals

Thank you. Om Namo Narayanaya!"""
                send_reply(msg["from"], greeting)
                return {"statusCode":200}

            reply = answer_user(msg["text"]["body"])
            short_reply = f"""{now:%I:%M %p}
{reply}"""
            send_reply(msg["from"], reply)

    return {"statusCode":200}