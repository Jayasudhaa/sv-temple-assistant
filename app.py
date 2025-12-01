# app.py
import json, os, urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo
from backend.ask_temple import answer_user

# --- ENV ---
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "svt-verify-123")
TOKEN        = os.getenv("WHATSAPP_ACCESS_TOKEN")
PHONE_ID     = os.getenv("WHATSAPP_PHONE_NUMBER_ID")


# ---------------------------------------------------------
# SEND WHATSAPP REPLY
# ---------------------------------------------------------
def send_reply(to, text):
    url = f"https://graph.facebook.com/v22.0/{PHONE_ID}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text[:1400]},
    }
    req = urllib.request.Request(url, json.dumps(payload).encode(), method="POST")
    req.add_header("Authorization", f"Bearer {TOKEN}")
    req.add_header("Content-Type", "application/json")

    try:
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        print("Send reply error:", e)


# ---------------------------------------------------------
# SIMPLE BULLET DEDUPE
# ---------------------------------------------------------
def dedupe_bullets(text: str) -> str:
    out, seen = [], set()
    for line in text.splitlines():
        clean = line.strip()
        norm = clean.lstrip("-• ").lower()
        if norm not in seen:
            seen.add(norm)
            out.append(clean)
    return "\n".join(out)


# ---------------------------------------------------------
# MAIN HANDLER
# ---------------------------------------------------------
def handler(event, context):

    # --- VALIDATION CALLBACK ---
    if event.get("httpMethod") == "GET":
        qs = event.get("queryStringParameters", {})
        if qs.get("hub.mode") == "subscribe" and qs.get("hub.verify_token") == VERIFY_TOKEN:
            return {"statusCode": 200, "body": qs.get("hub.challenge")}
        return {"statusCode": 403}

    # --- PARSE INCOMING MESSAGE ---
    body = json.loads(event.get("body", "{}"))

    for entry in body.get("entry", []):
        for change in entry.get("changes", []):
            msg = change.get("value", {}).get("messages", [{}])[0]
            if "text" not in msg:
                continue

            user_text = msg["text"]["body"].strip()
            lower = user_text.lower()
            sender = msg["from"]

            # -------------------------------------------------
            # THANK YOU RESPONSE
            # -------------------------------------------------
            if any(w in lower for w in ["thank", "thanks", "bye"]):
                send_reply(
                    sender,
                    "You're welcome! Blessings always.\nOm Namo Venkateshaya! Visit https://svtempleco.org/"
                )
                return {"statusCode": 200}

            # -------------------------------------------------
            # GREETING RESPONSE (FIXED - Word Boundary Check)
            # -------------------------------------------------
            # Check for greeting words that won't match inside other words
            greeting_words = ["hello", "namaste", "good morning", "good evening", "hey"]
            
            # For "hi", only match if it's a standalone word (not inside "abhishekam")
            is_greeting = False
            
            # Check for other greeting words
            if any(w in lower for w in greeting_words):
                is_greeting = True
            # Check for "hi" as standalone word only
            elif lower == "hi" or lower.startswith("hi ") or lower.endswith(" hi") or " hi " in lower:
                is_greeting = True
            
            if is_greeting:
                now = datetime.now(ZoneInfo("America/Denver"))
                current_month = now.strftime("%B")

                greeting = f"""🕉️ SV Temple Castle Rock, Colorado
{now:%A, %B %d, %Y} | {now:%I:%M %p %Z}
━━━━━━━━━━━━━━━━━━━━━━━
🙏 Namaste! Welcome to Sri Venkateswara Temple!

📍 Location: 1495 South Ridge Road, Castle Rock, CO 80104
📞 Phone: 303-898-5514 | Manager: 303-660-9555 🌐 www.svtempleco.org
⏰ TEMPLE HOURS:Weekdays: 9 AM-12 PM, 6 PM-8 PM,Weekends/Holidays: 9 AM-8 PM, Cafeteria: Sat-Sun 12 PM-2 PM

📅 SCHEDULES & PANCHANG:
• Daily Pooja (Suprabhata Seva, Nitya Archana),{current_month} Events & Festivals
• Satyanarayana Vratam Dates (Full Moon 6:30 PM),Today's Panchang (Tithi/Nakshatra),Specific date panchang (e.g., "Dec 1 panchang")

🪔 ABHISHEKAM SCHEDULE:
• 1st Week: Venkateswara (Sat), Siva (Sun)
• 2nd Week: Kalyanam (Sat), Ganapati/Murugan (Sun)
• 3rd Week: Andal (Fri), Mahalakshmi (Sat), Sai Baba (Sun)
• 4th Week: Hanuman (Sat), Sudarshana Homam (Sun)

🛕 ITEMS REQUIRED FOR POOJAS: Vahana Pooja (Vehicle Blessing), Satyanarayana Vratam,Abhishekam, Homam, Archana
💰 SERVICES & COSTS:
• Individual Pooja pricing,Arjitha Seva details, Abhishekam & Homam costs, Vahana Pooja (Walk-ins welcome!),Vastram Samarpanam sponsorship

👥 TEMPLE LEADERSHIP:
• Chairman: Saiganesh Rajamani (303-941-4166), President: Sri. Satyanarayana Velagapudi,• Manager: Sri. Nandu Sankaran (303-898-5514)
• Catering: Annapoorna Committee Chair: Smt. Swetha Sarvabhotla (537-462-6167)
💬 EXAMPLE QUERIES:
"When is Hanuman Abhishekam?"🕉️ Om Namo Venkateshaya! 🕉️
"""
                send_reply(sender, greeting)
                return {"statusCode": 200}

            # -------------------------------------------------
            # MAIN RAG + LLM PIPELINE
            # -------------------------------------------------
            now = datetime.now(ZoneInfo("America/Denver"))
            reply = answer_user(user_text)

            # dedupe bullets just in case
            reply = dedupe_bullets(reply)

            send_reply(sender, reply)

    return {"statusCode": 200}