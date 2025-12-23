# app.py - UPDATED with subscription and daily broadcast features
import json, os, urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo
from backend.ask_temple import answer_user
import boto3

# --- ENV ---
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "svt-verify-123")
TOKEN        = os.getenv("WHATSAPP_ACCESS_TOKEN")
PHONE_ID     = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

# --- DYNAMODB TABLES (NEW) ---
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
subscribers_table = dynamodb.Table('temple-subscribers')
events_table = dynamodb.Table('temple-events')


# ---------------------------------------------------------
# SEND WHATSAPP REPLY (EXISTING - NO CHANGES)
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
# DAILY BROADCAST SCRAPER (NEW)
# ---------------------------------------------------------
def scrape_and_broadcast():
    """
    Daily function: Scrape temple website and broadcast events
    Called by EventBridge at 9 AM
    """
    print("\n🕉️ STARTING DAILY EVENT BROADCAST")
    print("="*60)
    
    import requests
    from bs4 import BeautifulSoup
    from urllib.parse import urljoin
    import hashlib
    import time
    
    BASE_URL = "https://svtempleco.org"
    HOME_URL = f"{BASE_URL}/Home"
    
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Referer': 'https://svtempleco.org/'
    }
    
    EVENT_DATES = {
        'vaikuntaekadasi': 'December 30, 2025 (Tuesday)',
        'vaikunta ekadasi': 'December 30, 2025 (Tuesday)',
        'balavihar': 'January 2025 (Check with temple)',
        'melchat': 'January 2025 (Check with temple)'
    }
    
    # Get all active subscribers
    try:
        response = subscribers_table.scan(
            FilterExpression='subscribed = :val',
            ExpressionAttributeValues={':val': True}
        )
        subscribers = [item['phone_number'] for item in response.get('Items', [])]
        
        # Handle pagination
        while 'LastEvaluatedKey' in response:
            response = subscribers_table.scan(
                FilterExpression='subscribed = :val',
                ExpressionAttributeValues={':val': True},
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            subscribers.extend([item['phone_number'] for item in response.get('Items', [])])
        
        print(f"📱 Found {len(subscribers)} active subscribers")
        
        if not subscribers:
            print("⚠️ No subscribers found")
            return 0
            
    except Exception as e:
        print(f"❌ Error getting subscribers: {e}")
        return 0
    
    # Scrape website
    try:
        print("🔍 Scraping temple website...")
        session = requests.Session()
        session.headers.update(HEADERS)
        
        response = session.get(HOME_URL, timeout=30, allow_redirects=True)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        events = []
        
        event_imgs = soup.find_all('img', src=lambda x: x and 'eventSlider' in x)
        
        for img in event_imgs:
            src = img.get('src', '')
            if any(year in src.lower() for year in ['2025', '2026']):
                if src.startswith('../'):
                    img_url = urljoin(BASE_URL, src.replace('../', ''))
                elif src.startswith('/'):
                    img_url = BASE_URL + src
                else:
                    img_url = urljoin(HOME_URL, src)
                
                filename = src.split('/')[-1]
                event_name = filename.replace('.jpg', '').replace('.jpeg', '').replace('.png', '')
                event_name = event_name.replace('_', ' ').replace('2025', '').replace('2026', '').strip().title()
                
                events.append({
                    'filename': filename,
                    'name': event_name,
                    'image_url': img_url
                })
        
        print(f"✅ Found {len(events)} upcoming events")
        
    except Exception as e:
        print(f"❌ Scraping error: {e}")
        return 0
    
    if not events:
        print("ℹ️ No events to broadcast")
        return 0
    
    # Broadcast to subscribers
    events_posted = 0
    first_event = True
    
    for idx, event in enumerate(events):
        # Check if already posted
        event_hash = hashlib.md5(event['filename'].encode()).hexdigest()
        
        try:
            response = events_table.get_item(Key={'event_hash': event_hash})
            if 'Item' in response:
                print(f"⏭️ Skipping '{event['name']}' (already posted)")
                continue
        except:
            pass
        
        # Get event date
        event_lower = event['name'].lower()
        event_date = "Date TBD (Contact temple: 303-898-5514)"
        for key, date in EVENT_DATES.items():
            if key in event_lower:
                event_date = date
                break
        
        # Format message
        if first_event:
            message = f"""UPCOMING EVENTS

📅 {event['name']}
{event_date}"""
            first_event = False
        else:
            message = f"""📅 {event['name']}
{event_date}"""
        
        print(f"\n📢 Broadcasting: {event['name']}")
        
        # Send to all subscribers
        success_count = 0
        for phone in subscribers:
            if send_whatsapp_image(phone, event['image_url'], message):
                success_count += 1
            time.sleep(0.5)
        
        if success_count > 0:
            # Mark as posted
            try:
                events_table.put_item(
                    Item={
                        'event_hash': event_hash,
                        'event_data': json.dumps(event),
                        'timestamp': datetime.now().isoformat(),
                        'ttl': int(datetime.now().timestamp()) + (90 * 24 * 60 * 60)
                    }
                )
            except Exception as e:
                print(f"⚠️ Error marking as posted: {e}")
            
            events_posted += 1
            print(f"✅ Sent to {success_count}/{len(subscribers)} subscribers")
    
    # Send final welcome message
    if events_posted > 0:
        print("\n📢 Sending final welcome message...")
        welcome_msg = """All are Welcome.
Om Namo Venkateshaya 🕉️"""
        
        for phone in subscribers:
            send_reply(phone, welcome_msg)
            time.sleep(0.5)
    
    print(f"\n✅ BROADCAST COMPLETE: {events_posted} events posted")
    return events_posted


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
# MAIN HANDLER (UPDATED - Added EventBridge + Subscriptions)
# ---------------------------------------------------------
def handler(event, context):

    # -------------------------------------------------------
    # DAILY BROADCAST TRIGGER (NEW)
    # -------------------------------------------------------
    if event.get("source") == "aws.events":
        print("🔔 Triggered by EventBridge - Running daily broadcast")
        events_posted = scrape_and_broadcast()
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Daily broadcast completed',
                'events_posted': events_posted,
                'timestamp': datetime.now().isoformat()
            })
        }

    # --- VALIDATION CALLBACK (EXISTING - NO CHANGES) ---
    if event.get("httpMethod") == "GET":
        qs = event.get("queryStringParameters", {})
        if qs.get("hub.mode") == "subscribe" and qs.get("hub.verify_token") == VERIFY_TOKEN:
            return {"statusCode": 200, "body": qs.get("hub.challenge")}
        return {"statusCode": 403}

    # --- PARSE INCOMING MESSAGE (EXISTING - NO CHANGES) ---
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
            # SUBSCRIPTION COMMANDS (NEW)
            # -------------------------------------------------
            if lower in ["subscribe", "start", "join", "notifications"]:
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
                return {"statusCode": 200}
            
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
                return {"statusCode": 200}
            
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
                return {"statusCode": 200}

            # -------------------------------------------------
            # THANK YOU RESPONSE (EXISTING - NO CHANGES)
            # -------------------------------------------------
            if any(w in lower for w in ["thank", "thanks", "bye"]):
                send_reply(
                    sender,
                    "You're welcome! Blessings always.\nOm Namo Venkateshaya! Visit https://svtempleco.org/"
                )
                return {"statusCode": 200}

            # -------------------------------------------------
            # GREETING RESPONSE (EXISTING - NO CHANGES)
            # -------------------------------------------------
            greeting_words = ["hi", "hello", "hey", "namaste", "namaskar", "good morning", "good evening", "good afternoon", "namaskaram"]
            
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
📞 Phone: 303-898-5514 | Manager: 303-660-9555 🌐 www.svtempleco.org
⏰ TEMPLE HOURS:Weekdays: 9 AM-12 PM, 6PM-8 PM,Weekends/Holidays: 9 AM-8 PM, Cafeteria: Sat-Sun 12 PM-2 PM

📅 SCHEDULES & PANCHANG:
• Daily Pooja (Suprabhata Seva, Nitya Archana),{current_month} Events & Festivals
• Satyanarayana Vratam Dates,Today's Panchang (Tithi/Nakshatra),Specific date panchang (e.g., "Dec 1 panchang")

🪔 ABHISHEKAM SCHEDULE:
• 1st Week: Venkateswara (Sat), Siva (Sun)
• 2nd Week: Kalyanam (Sat), Ganapati/Murugan (Sun)
• 3rd Week: Andal (Fri), Mahalakshmi (Sat), Sai Baba (Sun)
• 4th Week: Hanuman (Sat), Sudarshana Homam (Sun)

🛕 ITEMS REQUIRED:Vahana Pooja (Vehicle Blessing), Satyanarayana Vratam,Abhishekam, Homam, Archana
💰 Sponsorship:• Individual Pooja pricing,Arjitha Seva details, Abhishekam & Homam costs,Vastram Samarpanam sponsorship

👥 TEMPLE LEADERSHIP:
• Chairman: Saiganesh Rajamani (303-941-4166), President: Sri. Satyanarayana Velagapudi,• Manager: Sri. Nandu Sankaran (303-898-5514)
• Catering: Annapoorna Committee Chair: Smt. Swetha Sarvabhotla (537-462-6167)
💬 EXAMPLE:"When is Hanuman Abhishekam?"
Type "subscribe" and send for notifications
🕉️ Om Namo Venkateshaya! 🕉️


"""
                send_reply(sender, greeting)
                return {"statusCode": 200}

            # -------------------------------------------------
            # MAIN RAG + LLM PIPELINE (EXISTING - NO CHANGES)
            # -------------------------------------------------
            now = datetime.now(ZoneInfo("America/Denver"))
            reply = answer_user(user_text, user_id=sender)

            # dedupe bullets just in case
            reply = dedupe_bullets(reply)

            send_reply(sender, reply)

    return {"statusCode": 200}
