"""
LOCAL TEST: Image Broadcast (NO AWS, NO WHATSAPP)

What this tests:
- Website scraping
- Event image extraction
- Caption formatting
- Broadcast loop
- Dedupe logic

What it DOES NOT do:
- No DynamoDB
- No WhatsApp API
"""

import json
import time
import hashlib
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime

# --------------------------------------------------
# MOCK CONFIG
# --------------------------------------------------
BASE_URL = "https://svtempleco.org"
HOME_URL = f"{BASE_URL}/Home"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "text/html,application/xhtml+xml",
}

# 👇 MOCK SUBSCRIBERS (EDIT FREELY)
MOCK_SUBSCRIBERS = [
    "17196391887"
]

# 👇 IN-MEMORY DEDUPE (simulates DynamoDB)
POSTED_EVENTS = set()


# --------------------------------------------------
# MOCK SEND IMAGE
# --------------------------------------------------
def send_whatsapp_image_mock(to, image_url, caption=""):
    print("\n📤 SEND IMAGE")
    print(f"➡️  To      : {to}")
    print(f"🖼️  Image   : {image_url}")
    print(f"📝 Caption : {caption}")
    return True


# --------------------------------------------------
# SCRAPE EVENTS
# --------------------------------------------------
def scrape_events():
    print("🔍 Scraping temple website...")
    response = requests.get(HOME_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    events = []

    KEYWORDS = [
        "festival", "utsav", "pooja", "homam",
        "kalyanam", "abhishekam", "shiv",
        "rama", "krishna", "event"
    ]

    image_urls = set()

    # 1️⃣ Normal <img src> and <img data-src>
    for img in soup.find_all("img"):
        for attr in ["src", "data-src"]:
            if img.has_attr(attr):
                image_urls.add(img[attr])

    # 2️⃣ Background images in inline styles
    for tag in soup.find_all(style=True):
        style = tag["style"]
        if "background-image" in style and "url(" in style:
            start = style.find("url(") + 4
            end = style.find(")", start)
            image_urls.add(style[start:end].strip("'\""))

    print(f"🔎 Found {len(image_urls)} raw image URLs")

    for raw in image_urls:
        src = raw.lower()

        if not any(k in src for k in KEYWORDS):
            continue

        # Normalize URL
        if raw.startswith("../"):
            img_url = urljoin(BASE_URL, raw.replace("../", ""))
        elif raw.startswith("/"):
            img_url = BASE_URL + raw
        elif raw.startswith("http"):
            img_url = raw
        else:
            img_url = urljoin(HOME_URL + "/", raw)

        filename = img_url.split("/")[-1].lower()

        name = (
            filename.replace(".jpg", "")
            .replace(".jpeg", "")
            .replace(".png", "")
            .replace("_", " ")
            .replace("-", " ")
            .title()
        )

        events.append({
            "filename": filename,
            "name": name,
            "image_url": img_url
        })

    print(f"✅ Extracted {len(events)} event images")
    return events



# --------------------------------------------------
# BROADCAST LOGIC
# --------------------------------------------------
def broadcast_images():
    print("\n🕉️ STARTING LOCAL IMAGE BROADCAST")
    print("=" * 60)

    events = scrape_events()
    if not events:
        print("⚠️ No events found")
        return

    first_event = True
    total_sent = 0

    for event in events:
        dedupe_key = f"{event['filename']}|{event['image_url']}|{event['name']}"
        event_hash = hashlib.md5(dedupe_key.encode()).hexdigest()

        if event_hash in POSTED_EVENTS:
            print(f"⏭️ Skipping duplicate: {event['name']}")
            continue

        if first_event:
            caption = f"UPCOMING EVENTS 📅 {event['name']}"
            first_event = False
        else:
            caption = f"📅 {event['name']}"

        print(f"\n📢 Broadcasting: {event['name']}")

        for phone in MOCK_SUBSCRIBERS:
            send_whatsapp_image_mock(phone, event["image_url"], caption)
            time.sleep(0.2)
            total_sent += 1

        POSTED_EVENTS.add(event_hash)

    print("\n📢 FINAL MESSAGE")
    for phone in MOCK_SUBSCRIBERS:
        print(f"➡️  To: {phone}")
        print("📝 All are Welcome. Om Namo Venkateshaya 🕉️")

    print("\n✅ BROADCAST COMPLETE")
    print(f"📦 Events sent   : {len(POSTED_EVENTS)}")
    print(f"📱 Messages sent : {total_sent}")


# --------------------------------------------------
# ENTRY POINT
# --------------------------------------------------
if __name__ == "__main__":
    broadcast_images()
