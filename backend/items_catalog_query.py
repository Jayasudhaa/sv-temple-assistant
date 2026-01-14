##backend/items_catalog_query.py

import datetime


# ============================================================
# ITEMS REQUIRED FOR POOJAS (Complete Temple Website Data)
# ============================================================

POOJA_SAMAGRI_URL = "https://svtempleco.org/Home/PoojaSamagri.html"

ITEMS_REQUIRED = {
    "general": {
        "name": "General Pooja Items",
        "items": """• Fresh flowers (jasmine, roses, or marigold)
• Fruits (banana, apple, orange - seasonal fruits)
• Coconut (1 whole)
• Betel leaves and betel nuts
• Turmeric and kumkum
• Incense sticks
• Camphor
• Ghee or oil for lamp""",
        "note": "Temple can provide most items for standard poojas"
    },

    "satyanarayana": {
        "name": "Satyanarayana Swamy Pooja at Temple",
        "items": """• Flowers - 3 Bunches
• Fruits - 3 varieties
• Betel leaves - 20 Nos.
• Coconuts - 8 Nos.
• Blouse piece - 1 No.
• Towel - 1 No.
• Milk (Organic) - 1 Gallon
• Ghee - 1 Lb
• Cashews - 1 Packet
• Sugar - 2 Lbs.
• Yogurt - 1 Box
• Honey - 1 Small bottle
• Turmeric and Kumkum - 1 Packet each
• Chandanam/Sandalwood powder - 1 Packet
• Camphor - 1 Packet
• Rice - 2 Lbs.
• Agarbatti/Incense sticks - 1 Packet
• Navadhanyam - 1 Packet
• Betel Nuts - 20 Nos.
• Dry Dates - 20 Nos.
• Quarter coins - 20 Nos.
• Mango leaves garland - 1 No.
• Rava Prasadam (Kesari)""",
        "note": "Full Moon Day at 6:30 PM"
    },

    "gruhapravesam": {
        "name": "Gruhapravesam (Housewarming) and Vastu Pooja",
        "items": """• Turmeric, Chandanam and Kumkuma - 1 Packet each
• Navadhanyalu - 1 Packet
• Milk - 0.5 gallon
• Curd - 1 Packet
• Honey - 1 small bottle
• Sugar - 0.5 lb
• Agarbatti, Karpuram/Camphor - 1 Packet each
• White Pumpkin Whole - 1 No.
• Rice - 2 Lbs
• Blouse piece - 1 No.
• Towel - 1 No.
• Navadhanyam - 1 Packet
• Quarter Coins - 40 Coins
• Rava Prasadam (Kesari)
• Betel Leaves - 20 Nos.
• Betel Nuts - 20 Nos.
• Fruits - 12 Bananas, 5 different varieties
• Flowers - 2 Bunches
• Coconut - 6 No.
• Dry Dates - 25 Nos.
• Lemons - 4 Nos.
• Hammer - 1 No.
• New Vessel for boiling milk - 1 No.
• Aluminum Trays - 4 Nos.
• Picture or Idol of a cow - 1 No.
• God Pictures - Your choice
• Lamps - 2 Nos. with wicks
• Matchbox or lighter - 1 No.
• Oil or Ghee for lamp
• Knife - 1 No.
• Scissors - 1 No.
• Mango leaves garland - 1 No.
• Flower garland - 1 No.
• Kalasam - 1 No.""",
        "note": "Contact temple in advance for home pooja arrangements"
    },

    "vastu": {
        "name": "Vastu Pooja",
        "items": """[Same as Gruhapravesam - see above]
Contact temple for specific Vastu Shanti requirements""",
        "note": "For Vastu Shanti. Contact for priest arrangement"
    },

    "homam": {
        "name": "Homam (Fire Ceremony)",
        "items": """• Dry coconuts - 6 Nos.
• Ghee - 1 Lb
• Cashews - 1 Packet
• Elaichi (Cardamom) - 1 Packet
• Silk blouse piece - 1 No.
• Big Aluminium trays - 5 Nos.
• Paper bowls - 5 Nos.
• Navadhanyam - 1 Packet
• Mango leaves garland - 1 No.""",
        "note": "Contact temple for specific homam requirements"
    },

    "archana": {
        "name": "Archana Items",
        "items": """• Fresh flowers (108 for 108 names)
• Fruits
• Coconut
• Betel leaves""",
        "note": "For special archana services"
    },

    "kalyanam": {
        "name": "Venkateswara Kalyanam (Divine Wedding)",
        "items": """• Milk (Organic) - 1/2 Gallon
• Coconuts - 3 Nos.
• Flower garlands - 3 Nos. (2.5 Feet long - 2 Nos., 3 Feet - 1 No.)
• Pattu (silk) sarees - 2 Nos. (applicable pattu saree to Venkateswara Swamy)
• Dry coconuts - 2 Nos.
• Betel leaves - 20 Nos.
• Betel Nuts - 20 Nos.
• Jeelakara Bellam (Cumin seeds and Jaggery) - 1 small packet each
• Agarbatti/Incense sticks, Karpuram/Camphor - 1 Packet each
• Turmeric, Chandanam and Kumkum - 1 Packet each
• Rice - 2 Kgs.
• Flowers - 2 bunches
• Fruits - 5 different
• Blouse Piece - 2 No.
• Honey - 1 small bottle
• Talambralu (Raw turmeric rice) - 1.5 Kgs

IN ADDITION (if done at home):
• Curd - 1 No
• Steel plates - 4 No.
• Kalasam - 2 No.
• Panchapatra - 2 No.
• Udharani (spoons) - 2 No.
• Mango Leaves - One bunch""",
        "note": "2nd Week Saturday 11:00 AM"
    },

    "bhoomi_pooja": {
        "name": "Bhoomi Pooja (Foundation Ceremony)",
        "items": """• Turmeric, Chandanam and Kumkuma - 1 Packet each
• Agarbatti, Karpuram/Camphor, Match Box - 1 Packet each
• Rice - 1.5 Kgs
• Towels - 2 Nos.
• Blouse piece - 1 No.
• Navadhanyam - 2 Packet
• Navarathnalu - 1 Packet (Optional)
• Quarter coins - 25 Nos.
• Betel leaves - 15 Nos.
• Betel Nuts - 15 Nos.
• Coconuts - 4 Nos.
• Flowers - 2 Bunches
• Fruits - 3 Varieties
• Bricks (any color) - 9 Nos.
• Mango Leaves - One bunch""",
        "note": "For new construction foundation ceremony"
    },

    "annaprasana": {
        "name": "Anna Prasana (First Rice Ceremony)",
        "items": """• Turmeric, Chandanam and Sindhuram - 1 Packet each
• Agarbatti, Karpuram/Camphor, Match Box - 1 Packet each
• Rice - 1 Lb
• Blouse piece - 1 No.
• Betel leaves - 10 Nos.
• Betel Nuts - 10 Nos.
• Coconuts - 2 Nos.
• Flowers - 1 Bunch
• Fruits - 12 Bananas, 1 Orange bag
• Ghee or Sesame Oil - 1 Small bottle
• Sweet payasam - Just for feeding baby
• Mango Leaves - One bunch""",
        "note": "Baby's first solid food ceremony"
    },

    "namakaranam": {
        "name": "Namakaranam (Naming Ceremony)",
        "items": """• Turmeric, Chandanam and Sindhuram - 1 Packet each
• Agarbatti, Karpuram/Camphor, Match Box - 1 Packet each
• Rice - 1 Lb
• Betel leaves - 10 Nos.
• Betel Nuts - 10 Nos.
• Coconuts - 2 Nos.
• Flowers - 1 Bunch
• Fruits - 12 Bananas, 1 Orange bag
• Honey - 1 Small bottle
• Quarter Coins - 20 Nos.
• Milk (Organic) - 1 Gallon
• Dry Dates - 10 Nos.
• Mango Leaves - One bunch""",
        "note": "Baby naming ceremony"
    },

    "hair_offering": {
        "name": "Hair Offering (Mundan)",
        "items": """• Turmeric, Chandanam and Kumkuma - 1 Packet each
• Agarbatti, Karpuram/Camphor, Match Box - 1 Packet each
• Rice - 1 Lb
• Yellow Cloth - 1 Yard
• Betel leaves - 10 Nos.
• Betel Nuts - 10 Nos.
• Scissors - 1 No.
• Flowers - 1 Bunch
• Fruits - 12 Bananas, 1 Orange bag
• Quarter Coins - 10 Nos.
• Milk (Organic) - 1 Gallon""",
        "note": "Child's first hair offering ceremony"
    },

    "seemantham": {
        "name": "Seemantham (Baby Shower)",
        "items": """• Turmeric, Chandanam and Kumkuma - 1 Packet each
• Agarbatti, Karpuram/Camphor, Match Box - 1 Packet each
• Rice - 2 Lbs
• Coconuts - 2 Nos.
• Small Mirror and Comb - 1 No. each
• Flowers - 1 Bunch
• Fruits - 12 Bananas, 1 Orange bag
• Sumangali Sets (Turmeric & Kumkum, Blouse piece, Comb, Bangles) - 7 Sets
• Milk (Organic) - 1 Gallon
• Mango leaves - One bunch""",
        "note": "Traditional baby shower ceremony for pregnant women"
    },

    "nischitartham": {
        "name": "Nischitartham (Engagement Ceremony)",
        "items": """• Turmeric and Kumkum - 2 Cups each
• Agarbatti, Karpuram/Camphor - 2 Packets each
• Rice - 3 Lbs
• Blouse piece - 2 Nos.
• Betel leaves and Nuts - 20 Nos.
• Coconuts - 4 Nos.
• Flower Garlands - 2 Nos. Grand malas, 2+2 for both parents
• Loose Flower - 1 bunch
• Fruits - 5 varieties, 5 plates full
• Quarter Coins - 11 Nos.
• Chandanam - 1 Packet
• Lakshmi photo and any other photos - 1 + 1 Nos.
• Mango Leaves (if available) - 1 Bunch
• Kitchen Paper Towel - 1 Roll
• Oil Lamps - 2 Nos.
• Wooden planks to sit for pooja - 3 Nos.
• Any Sweet Prasadam - 1 Bowl
• Steel Glass with Spoons - 2 Nos.
• Kalasam Chembu - 1 No.
• Different varieties of Phalagarams (Muruku, Paruputhenga, Sweets etc.) - 4 Plates full
• New dress for the Groom and his parents
• New dress for the Bride and her parents
• Coconuts powder mixed with sugar candy and sugar powder""",
        "note": "Hindu engagement ceremony. Contact temple for priest arrangement"
    },

    "hindu_wedding": {
        "name": "Hindu Wedding Ceremony",
        "items": """• Turmeric and Kumkum - 1 Packet each
• Betel Leaves and Nuts - 20 Nos. each
• Dry Turmeric Root - 1 Packet
• Dry Dates - 1 Packet
• Agarbatti/Incense sticks, Karpuram/Camphor - 1 Packet each
• Rice - 20 Lbs
• Cloth Towels - 2 Nos.
• Sandal Powder - 1 Packet
• Jeera - 1 Packet
• Jaggery - 1 Packet
• Ghee - 250 Grams
• Dry Coconut Halves - 4 Nos.
• Coconuts - 4 Nos.
• Blouse Pieces - 2 Nos.
• Mangalyam/Mangalasutra - 1 Set
• Quarter Coins - 28 Nos. (and 40 for Telugu weddings)
• Cotton Thread - 1 No.
• Steel/Glass Tumblers - 4 Nos.
• Ring for the Groom - Optional
• Big Steel Plate for Pada Pooja (Tray size) - 1 No.
• Flower Garlands - 2 Nos.
• Silk clothes for Bride and Groom
• Flowers - 3 bunches
• Brass/Silver/Gold plate for washing Bride
• Kalasam - 3 No.
• Plates - 4 No.
• Paper bowls - 10 No.
• Deepam Kundulu (Lamp/Vellekku) - 2 Nos.
• Vathulu - 1 No.
• Sesame oil - 1 No.
• White clothes - 2 No (each 3 or 4 yards)
• Steel Binde - 1 (for Telugu weddings)""",
        "note": "Complete Hindu wedding ceremony. Contact temple well in advance"
    },

    "hiranya_sharddham": {
        "name": "Hiranya Sharddham",
        "items": """• Flowers and Fruits
• Betel Leaves and Nuts - 10 Nos. each
• Rice - 1 Bag
• Black Sesame Seeds - 1 Small Packet
• Moong Dal - 1 Small Packet
• Urad Dal - 1 Small Packet
• Oil - 1 Small Bottle
• Jeera - 1 Small Packet
• Red Chilly - 1 Small Packet
• Tamarind - 1 Small Packet
• Jaggery - 1 Small Packet
• Ghee - 1 Bottle
• Vegetables - Mixed
• Milk (Organic) - 1 Gallon
• Quarter Coins - 10 Nos.""",
        "note": "Memorial ritual for departed souls. Contact temple for scheduling"
    },

    "nava_graha": {
        "name": "Nava Graha Pooja (Nine Planets)",
        "items": """• Sani Graha: Black sesame seeds 50 grams, Sesame oil, Fruits & Flowers
• Rahuvu Graha: Whole Urad 50 grams (Minumalu), Sesame oil, Fruits & Flowers
• Ketuvu Graha: Horse gram 50 grams (Ulavalu), Sesame oil, Fruits & Flowers
• Surya Graha: Wheat 50 grams, Sesame oil, Fruits & Flowers
• Chandra Graha: Rice 50 grams, Sesame oil, Fruits & Flowers
• Angaraka Graha: Whole lentil 50 grams (Kandulu), Fruits & Flowers
• Budha Graha: Whole Moong 50 grams (Pesalu), Fruits & Flowers
• Guru Graha: Senagalu 50 grams, Sesame oil, Fruits & Flowers
• Sukra Graha: White Black eye peas 50 grams (white Bobbarlu), Sesame oil, Fruits & Flowers""",
        "note": "Planetary worship for removing obstacles and planetary doshas"
    },

    "aksharabhyasam": {
        "name": "Aksharabhyasam (Vidyarambham)",
        "items": """• Fruits - 12 Bananas, 1 Bag of Oranges
• Betel Leaves and Nuts - 10 Nos. each
• Rice - 1 Lb
• Flowers - 1 Bunch
• Turmeric, Kumkum and Chandanam - 1 Packet each
• Agarbatti and Camphor - 1 Packet each
• Dry Dates - 10 Nos.
• Coconut - 2 Nos.
• Slate - 1 No.
• Chalk - 1 No.
• Notebook - 2 Nos.
• Pen - 1 No.
• Ghee or Oil - 1 Bottle
• Milk (Organic) - 1 Gallon
• Quarter Coins - 20 Nos.
• Mango Leaves - One bunch""",
        "note": "Child's educational initiation ceremony (first writing)"
    },

    "abhishekam": {
        "name": "Abhishekam Items",
        "items": """• Fruits - 12 Bananas, 1 Bag of Oranges
• Sugar - 1 Small Packet
• Rice - 1 Lb
• Flowers - 1 Bunch
• Turmeric, Kumkum and Chandanam - 1 Packet each
• Agarbatti and Camphor - 1 Packet each
• Honey - 1 Bottle
• Coconut - 3 Nos.
• Coconut Water - 1 Big Bottle
• Any Variety of Juice - 1 Gal
• Ghee - 1 Bottle
• Milk (Organic) - 1 Gallon
• Organic Yogurt - 1/4 Gallon""",
        "note": "Check weekly abhishekam schedule. Complete ritual bathing of deity"
    },

    "half_saree": {
        "name": "Half Saree Function (Ritu Kala Samskara)",
        "items": """• Turmeric, Kumkum and Chandanam - 1 Packet each
• Agarbatti and Camphor - 1 Packet each
• Fruits - 3 Varieties
• Flowers - Your choice
• Rice - 2 Lbs
• Coconut - 2 Nos.
• Blouse Piece - 2 Nos.
• Betel Leaves - 8 Nos.
• Betel Nuts - 1 Packet
• Quarter Coins - 25 Nos.
• Dry Fruits - 1 Packet
• Mango Leaves - One bunch
• Half saree - 1 No.
• Kalasam - 1 No.""",
        "note": "Traditional coming-of-age ceremony for young girls"
    },

    "any_homam": {
        "name": "Any Homam (General Requirements)",
        "items": """• Turmeric and Kumkum - 1 Small Packet each
• Betel Leaves and Nuts - 10 Nos. each
• Flowers - 2 Bunches
• Agarbatti/Incense sticks, Karpuram/Camphor - 1 Small Packet each
• Rice - 1 Lb
• Coconuts - 3 Nos.
• Dry Coconuts - 6 Packets
• Navadhanyam - 1 Small Packet
• Blouse Piece - 1 No.
• Kalasam - 1 No. (Skip if pooja is at temple)
• Cups and Plates (Skip if pooja is at temple)
• Ghee - 1 Bottle
• Fruits - 2 Varieties
• Sweet Prasadham (Skip if pooja is at temple)
• Mango Sticks - 3 Packets
• Silk Blouse Piece - 1 No.
• Quarter Coins - 20 Nos.
• Mango Leaves - One bunch""",
        "note": "General items for any homam. Contact temple for specific homam requirements"
    },

    "sudarshana": {
        "name": "Sudarshana Homam",
        "items": """• Dry coconuts - 6 Nos.
• Ghee - 1 Lb
• Cashews - 1 Packet
• Elaichi - 1 Packet
• Navadhanyam - 1 Packet
• Mango leaves garland
• Aluminium trays - 5 Nos.
• Paper bowls - 5 Nos.
• Sacred wood
• Sesame seeds""",
        "note": "4th Week Sunday 11:00 AM"
    }
}

ITEM_KEYS = {
    key.replace("_", " "): key
    for key in ITEMS_REQUIRED
}

def handle_items_required(q: str, now: datetime) -> str | None:
    if not any(w in q for w in ["item", "items", "bring", "required", "need", "samagri", "material"]):
        return None

    # --------------------------------------------------
    # 1️⃣ ANY DEITY ABHISHEKAM → SAME ITEMS
    # --------------------------------------------------
    if "abhishekam" in q:
        info = ITEMS_REQUIRED["abhishekam"]
        return (
            "Om Namo Venkateshaya 🙏\n\n"
            "🪔 ITEMS REQUIRED FOR ABHISHEKAM\n\n"
            f"{info['items']}\n\n"
            "📌 These items are COMMON for ALL Abhishekams:\n"
            "• Siva Abhishekam\n"
            "• Ganapati Abhishekam\n"
            "• Murugan Abhishekam\n"
            "• Hanuman Abhishekam\n"
            "• Sai Baba Abhishekam\n"
            "• Raghavendra Swamy Abhishekam\n"
            "• Venkateswara Swamy Abhishekam\n\n"
            f"📌 {info['note']}\n"
            f"🔗 {POOJA_SAMAGRI_URL}\n\n"
            
        )
    
    # --------------------------------------------------
    # 1️⃣ SPECIAL CASE: AKSHARABHYASAM (MULTIPLE NAMES)
    # --------------------------------------------------
    if any(w in q for w in [
        "aksharabhyasam",
        "akshara abhyasam",
        "vidyarambham",
        "vidya arambham",
        "first writing"
    ]):
        info = ITEMS_REQUIRED["aksharabhyasam"]
        return (
            "Om Namo Venkateshaya 🙏\n\n"
            f"🪔 {info['name'].upper()}\n\n"
            f"{info['items']}\n\n"
            f"📌 {info['note']}\n"
            f"🔗 {POOJA_SAMAGRI_URL}\n\n"
        )


    # --------------------------------------------------
    # 2️⃣ DIRECT ITEM KEYS (Satyanarayana, Gruhapravesam, etc.)
    # --------------------------------------------------
    for phrase, key in ITEM_KEYS.items():
        if phrase in q:
            info = ITEMS_REQUIRED[key]
            return (
                "Om Namo Venkateshaya 🙏\n\n"
                f"🪔 {info['name'].upper()}\n\n"
                f"{info['items']}\n\n"
                f"📌 {info['note']}\n"
                f"🔗 {POOJA_SAMAGRI_URL}\n\n"
                
            )

    # --------------------------------------------------
    # 3️⃣ FALLBACK – SHOW VALID OPTIONS (NO GENERIC GARBAGE)
    # --------------------------------------------------
    valid = sorted([

        "Abhishekam (all deities)",
        "Satyanarayana Pooja",
        "Homam",
        "Sudarshana Homam",
        "Vastu Pooja",
        "Nava Graha Pooja",

        # Life events / samskaras
        "Gruhapravesam",
        "Bhoomi Pooja",
        "Hindu Wedding",
        "Engagement (Nischitartham)",
        "Kalyanam",
        "Half Saree Function",
        "Aksharabhyasam",
        "Namakaranam",
        "Annaprasana",
        "Seemantham",
        "Hair Offering (Mundan)",
        "Hiranya Shraddham",
    ])

    return (
        "Om Namo Venkateshaya 🙏\n\n"
        "🪔 POOJA ITEMS INFORMATION\n\n"
        "Please specify one of the following:\n\n"
        + "\n".join(f"• {v}" for v in valid)
        + "\n\n"
        )
