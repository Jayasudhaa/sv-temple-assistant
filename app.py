# app.py - UPDATED with subscription and daily broadcast features
import json, os, urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo
from backend.ask_temple import answer_user
import re
import boto3
import logging,hashlib
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# --- ENV ---
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "svt-verify-123")
TOKEN        = os.getenv("WHATSAPP_ACCESS_TOKEN")
PHONE_ID     = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

# --- DYNAMODB TABLES (NEW) ---
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
subscribers_table = dynamodb.Table('temple-subscribers')



# ---------------------------------------------------------
# SEND WHATSAPP REPLY (EXISTING - NO CHANGES)
# ---------------------------------------------------------
def send_reply(to, text):
    prefix = "Om Namo Venkateshaya 🙏\n\n"

    # Avoid double prefix
    if not text.strip().lower().startswith("om namo venkateshaya"):
        text = prefix + text

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
# SEND WHATSAPP IMAGE (NEW)
# ---------------------------------------------------------
def send_whatsapp_image(to, image_url, caption=""):
    """Send WhatsApp image with caption"""
    url = f"https://graph.facebook.com/v22.0/{PHONE_ID}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "image",
        "image": {
            "link": image_url,
            "caption": caption[:1024] if caption else ""
        }
    }
    req = urllib.request.Request(url, json.dumps(payload).encode(), method="POST")
    req.add_header("Authorization", f"Bearer {TOKEN}")
    req.add_header("Content-Type", "application/json")

    try:
        urllib.request.urlopen(req, timeout=10)
        return True
    except Exception as e:
        print("Send image error:", e)
        return False


# ---------------------------------------------------------
# SEND WHATSAPP QUICK BUTTONS (INTERACTIVE)
# ---------------------------------------------------------
def send_quick_buttons(to, body_text="Choose an option:"):
    """
    Sends a WhatsApp Interactive Button message (Quick Reply buttons).
    Buttons appear under that single message (not permanent UI).
    """
    url = f"https://graph.facebook.com/v22.0/{PHONE_ID}/messages"

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": body_text[:1024]},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": "BTN_HOURS", "title": "⏰Temple Hours"}},
                    {"type": "reply", "reply": {"id": "BTN_EVENTS_TODAY", "title": "📅Events Today"}},
                ]
            },
        },
    }

    req = urllib.request.Request(url, json.dumps(payload).encode(), method="POST")
    req.add_header("Authorization", f"Bearer {TOKEN}")
    req.add_header("Content-Type", "application/json")

    try:
        urllib.request.urlopen(req, timeout=10)
        return True
    except Exception as e:
        print("Send buttons error:", e)
        return False

# ---------------------------------------------------------
# SEND WHATSAPP QUICK BUTTONS (INTERACTIVE)
# ---------------------------------------------------------
def send_subscribe_button(to, body_text="Choose an option:"):
    """
    Sends a WhatsApp Interactive Button message (Quick Reply buttons).
    Buttons appear under that single message (not permanent UI).
    """
    url = f"https://graph.facebook.com/v22.0/{PHONE_ID}/messages"

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": body_text[:1024]},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": "BTN_SUBSCRIBE", "title": "🔔Subscribe"}},
                    ]
            },
        },
    }

    req = urllib.request.Request(url, json.dumps(payload).encode(), method="POST")
    req.add_header("Authorization", f"Bearer {TOKEN}")
    req.add_header("Content-Type", "application/json")

    try:
        urllib.request.urlopen(req, timeout=10)
        return True
    except Exception as e:
        print("Send buttons error:", e)
        return False
# ---------------------------------------------------------
# SUBSCRIPTION MANAGEMENT (NEW)
# ---------------------------------------------------------
def subscribe_user(phone_number):
    """Add user to subscription list"""
    try:
        subscribers_table.put_item(
            Item={
                'phone_number': phone_number,
                'subscribed': True,
                'subscribed_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
        )
        print(f"✅ Subscribed: {phone_number}")
        return True
    except Exception as e:
        print(f"❌ Error subscribing: {e}")
        return False


def unsubscribe_user(phone_number):
    """Remove user from subscription list"""
    try:
        subscribers_table.update_item(
            Key={'phone_number': phone_number},
            UpdateExpression='SET subscribed = :val, updated_at = :time',
            ExpressionAttributeValues={
                ':val': False,
                ':time': datetime.now().isoformat()
            }
        )
        print(f"✅ Unsubscribed: {phone_number}")
        return True
    except Exception as e:
        print(f"❌ Error unsubscribing: {e}")
        return False


def check_subscription(phone_number):
    """Check if user is subscribed"""
    try:
        response = subscribers_table.get_item(Key={'phone_number': phone_number})
        if 'Item' in response:
            return response['Item'].get('subscribed', False)
        return False
    except Exception as e:
        print(f"❌ Error checking subscription: {e}")
        return False

# ---------------------------------------------------------
# SIMPLE BULLET DEDUPE (EXISTING - NO CHANGES)
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
# EXTRACT USER MESSAGE TEXT (TEXT + BUTTON REPLIES)
# ---------------------------------------------------------
def extract_user_message(msg: dict) -> str | None:
    """
    Supports:
    - Normal text messages
    - Interactive button replies
    """
    # Normal text
    if msg.get("type") == "text" and "text" in msg:
        return msg["text"]["body"].strip()

    # Interactive button click
    if msg.get("type") == "interactive":
        interactive = msg.get("interactive", {})
        if interactive.get("type") == "button_reply":
            btn = interactive.get("button_reply", {})
            # Prefer ID (stable), fallback to title
            return (btn.get("id") or btn.get("title") or "").strip()

    return None


# ---------------------------------------------------------
# MAP BUTTON IDs TO REAL QUERIES
# ---------------------------------------------------------
BUTTON_MAP = {
    "BTN_SUBSCRIBE": "subscribe",
    "BTN_HOURS": "temple hours",
    "BTN_EVENTS_TODAY": "events today",
}
# ---------------------------------------------------------
# MAIN HANDLER (UPDATED - Added EventBridge + Subscriptions)
# ---------------------------------------------------------
def handler(event, context):

    # --- VALIDATION CALLBACK (GET) ---
    if event.get("httpMethod") == "GET":
        qs = event.get("queryStringParameters", {}) or {}
        if qs.get("hub.mode") == "subscribe" and qs.get("hub.verify_token") == VERIFY_TOKEN:
            return {"statusCode": 200, "body": qs.get("hub.challenge")}
        return {"statusCode": 403}

    # --- POST ---
    try:
        body = json.loads(event.get("body", "{}") or "{}")
    except Exception:
        return {"statusCode": 200}

    for entry in body.get("entry", []):
        for change in entry.get("changes", []):
            messages = change.get("value", {}).get("messages", [])
            if not messages:
                continue

            for msg in messages:
                sender = msg.get("from")
                if not sender:
                    continue

                user_text = extract_user_message(msg)
                if not user_text:
                    continue

                # If user clicked a button: ID -> command
                user_text = BUTTON_MAP.get(user_text, user_text)
                lower = user_text.lower().strip()

                # -------------------------------------------------
                # QUICK SHORTCUT WORDS (events/hours/help/menu)
                # -------------------------------------------------
                if lower in ["help", "menu", "options", "start"]:
                    send_reply(sender, "• Please choose an option below.")
                    send_quick_buttons(sender, "Choose an option:")
                    continue

                if lower in ["events", "event", "schedule"]:
                    user_text = "events today"
                    lower = "events today"

                if lower in ["hours", "timings", "timing", "time"]:
                    user_text = "temple hours"
                    lower = "temple hours"

                # -------------------------------------------------
                # SUBSCRIPTION COMMANDS
                # -------------------------------------------------
                if lower in ["subscribe", "join", "notifications"]:
                    success = subscribe_user(sender)
                    if success:
                        send_reply(
                            sender,
                            "✅ Subscribed Successfully!\n\n"
                            "You will receive notifications about upcoming temple events.\n\n"
                            "📅 Daily event updates at 9 AM\n"
                            "🕉️ Special festival announcements\n\n"
                            "Commands:\n"
                            "• unsubscribe - Stop notifications\n"
                            "• status - Check subscription\n\n"
                            "Om Namo Venkateshaya 🕉️"
                        )
                    else:
                        send_reply(sender, "❌ Subscription failed. Please try again.")
                    continue

                if lower in ["unsubscribe", "stop", "leave", "cancel"]:
                    success = unsubscribe_user(sender)
                    if success:
                        send_reply(
                            sender,
                            "✅ Unsubscribed Successfully\n\n"
                            "You will no longer receive event notifications.\n\n"
                            "To subscribe again, send: subscribe\n\n"
                            "Om Namo Venkateshaya 🕉️"
                        )
                    else:
                        send_reply(sender, "❌ Unsubscribe failed. Please try again.")
                    continue

                if lower in ["status", "check", "subscription"]:
                    is_subscribed = check_subscription(sender)
                    if is_subscribed:
                        send_reply(
                            sender,
                            "📊 Subscription Status: ✅ ACTIVE\n\n"
                            "You are receiving event notifications.\n\n"
                            "To unsubscribe, send: unsubscribe"
                        )
                    else:
                        send_reply(
                            sender,
                            "📊 Subscription Status: ❌ INACTIVE\n\n"
                            "You are not receiving notifications.\n\n"
                            "To subscribe, send: subscribe"
                        )
                    continue

                # -------------------------------------------------
                # THANK YOU RESPONSE
                # -------------------------------------------------
                if re.search(r"\b(thanks|thank you|bye|goodbye)\b", lower):
                    send_reply(
                        sender,
                        "You're welcome! Blessings always.\n"
                        "Om Namo Venkateshaya! Visit https://svtempleco.org/"
                    )
                    continue

                # -------------------------------------------------
                # GREETING RESPONSE
                # -------------------------------------------------
                greeting_words = [
                    "hi", "hello", "hey", "namaste", "namaskar",
                    "good morning", "good evening", "good afternoon", "namaskaram"
                ]

                is_pure_greeting = False
                if lower in greeting_words:
                    is_pure_greeting = True
                elif lower.startswith(("good morning", "good evening", "good afternoon")):
                    first_two_words = " ".join(lower.split()[:2])
                    if first_two_words in greeting_words:
                        is_pure_greeting = True

                if is_pure_greeting:
                    now = datetime.now(ZoneInfo("America/Denver"))
                    current_month = now.strftime("%B")

                    greeting = f"""🕉️ SV Temple Castle Rock, Colorado
{now:%A, %B %d, %Y} | {now:%I:%M %p %Z}
────────────────────────
🙏 Namaste! Welcome to Sri Venkateswara Temple!
📍 Location: 1495 South Ridge Road, Castle Rock, CO 80104
📞 Manager: 303-898-5514 | Phone: 303-660-9555 🌐 www.svtempleco.org
⏰ TEMPLE HOURS: Weekdays: 9 AM-12 PM, 6 PM-8 PM | Weekends/Holidays: 9 AM-8 PM
Cafeteria: Sat-Sun 12 PM-2 PM

Type "subscribe" and send for notifications

📅 SCHEDULES & PANCHANG:
• Daily Pooja (Suprabhata Seva, Nitya Archana), {current_month} Events & Festivals
• Satyanarayana Vratam Dates
• Today's Panchang (Tithi/Nakshatra)
• Specific date panchang (e.g., "Dec 1 panchang")

💬 EXAMPLE: "When is Hanuman Abhishekam?"

🕉️ Om Namo Venkateshaya! 🕉️
"""
                    send_reply(sender, greeting)

                    # ✅ Show buttons right after greeting


                    send_quick_buttons(sender, "Quick options:")
                    if not check_subscription(sender):
                        send_subscribe_button(sender, "Please subscribe:")

                    continue

                # ✅ Structured analytics log (1 line per query)
                user_hash = hashlib.sha256(sender.encode()).hexdigest()[:10]  # avoids storing phone number directly

                logger.info(json.dumps({
                    "event": "query",
                    "user": user_hash,
                    "query": user_text,
                    "query_lc": lower,
                    "ts": datetime.now(ZoneInfo("America/Denver")).isoformat(),
                    "channel": "whatsapp"
                }))


                # -------------------------------------------------
                # MAIN RAG + LLM PIPELINE
                # -------------------------------------------------
                reply = answer_user(user_text, user_id=sender)
                reply = dedupe_bullets(reply)

                send_reply(sender, reply)

                # ✅ Show buttons after answering
                if not check_subscription(sender):
                    send_subscribe_button(sender, "Please subscribe:")

    return {"statusCode": 200}
