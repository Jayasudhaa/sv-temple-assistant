# app.py - UPDATED with subscription and daily broadcast features
import json, os, urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo
from backend.ask_temple import answer_user
import boto3

# =========================
# DUPLICATE MESSAGE GUARD
# =========================
PROCESSED_MESSAGE_IDS = set()

# --- ENV ---
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "svt-verify-123")
TOKEN        = os.getenv("WHATSAPP_ACCESS_TOKEN")

WHATSAPP_PHONE_IDS = {
    pid.strip() for pid in os.getenv("WHATSAPP_PHONE_NUMBER_IDS", "").split(",") if pid.strip()
}
if not WHATSAPP_PHONE_IDS:
    raise RuntimeError("❌ WHATSAPP_PHONE_NUMBER_IDS is empty or not set")

BROADCAST_PHONE_ID = next(iter(WHATSAPP_PHONE_IDS))

# --- DYNAMODB TABLES ---
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
subscribers_table = dynamodb.Table('temple-subscribers')
events_table = dynamodb.Table('temple-events')


# ---------------------------------------------------------
# SEND WHATSAPP REPLY
# ---------------------------------------------------------
def send_reply(phone_id: str, to: str, text: str):
    prefix = "Om Namo Venkateshaya 🙏\n\n"
    if not text.strip().lower().startswith("om namo venkateshaya"):
        text = prefix + text

    url = f"https://graph.facebook.com/v22.0/{phone_id}/messages"
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
        print("❌ send_reply error:", e)


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

    # DAILY BROADCAST
    if event.get("source") == "aws.events":
        return {"statusCode": 200}

    # VALIDATION CALLBACK
    if event.get("httpMethod") == "GET":
        qs = event.get("queryStringParameters", {})
        if qs.get("hub.mode") == "subscribe" and qs.get("hub.verify_token") == VERIFY_TOKEN:
            return {"statusCode": 200, "body": qs.get("hub.challenge")}
        return {"statusCode": 403}

    body = json.loads(event.get("body", "{}"))

    for entry in body.get("entry", []):
        for change in entry.get("changes", []):
            messages = change.get("value", {}).get("messages", [])
            if not messages:
                continue

            msg = messages[0]

            # =========================
            # DUPLICATE MESSAGE FIX
            # =========================
            msg_id = msg.get("id")
            if not msg_id:
                continue

            if msg_id in PROCESSED_MESSAGE_IDS:
                print(f"⏭️ Duplicate message ignored: {msg_id}")
                continue

            PROCESSED_MESSAGE_IDS.add(msg_id)
            # =========================

            metadata = change.get("value", {}).get("metadata", {})
            incoming_phone_id = metadata.get("phone_number_id")

            if incoming_phone_id not in WHATSAPP_PHONE_IDS:
                continue
            if "text" not in msg:
                continue

            user_text = msg["text"]["body"].strip()
            sender = msg["from"]

            reply = answer_user(user_text, user_id=sender)
            reply = dedupe_bullets(reply)

            send_reply(incoming_phone_id, sender, reply)

            return {"statusCode": 200}

    return {"statusCode": 200}
