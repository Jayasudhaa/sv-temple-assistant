# backend/ask_temple.py

import os, json, re, boto3
from datetime import datetime
from zoneinfo import ZoneInfo
from .retrieval import get_chunks

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

    "vahana": {
        "name": "Vahana Pooja (Vehicle Blessing)",
        "items": """• Lemons
• 1 Coconut
• Fruits
• Flowers""",
        "note": "Walk-ins welcome subject to priest availability"
    },

    "satyanarayana_temple": {
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

    "satyanarayana_home": {
        "name": "Satyanarayana Swamy Pooja at Home",
        "items": """• Flowers - 3 Bunches
• Fruits - 3 varieties
• Betel leaves - 20 Nos.
• Coconuts - 8 Nos.
• Blouse piece - 1 No.
• Towel - 1 No.
• Milk (Organic) - 1 Gallon
• Rava Prasadam - As required
• Ghee - 1 Lb
• Cashews - 1 Packet
• Sugar - 2 Lbs.
• Yogurt - 1 Box
• Honey - 1 Lb
• Turmeric and Kumkum - 1 Packet each
• Chandanam/Sandalwood powder - 1 Packet
• Camphor - 1 Packet
• Rice - 2 Lbs.
• Agarbatti/Incense sticks - 1 Packet
• Navadhanyam - 1 Packet
• Betel Nuts - 20 Nos.
• Dry Dates - 20 Nos.
• Satyanarayana Swamy Photo - 1 No.
• Small table - 1 No.
• Steel bowls - 2 Nos.
• Hammer - 1 (to break coconuts)
• Haarati/Aarti plate - 1 No.
• Lamps with cotton wicks - 2 Nos.
• Sesame Oil - For lamps
• Matchbox/lighter - 1 No.
• Kalasam - 1 No.
• Panchapara (glass) and Uddarini (spoon) - 1 No. each
• Small trays - 2 Nos.
• Big trays - 2 Nos.
• Small cups - 5 Nos.
• Spoons and napkins - As required""",
        "note": "For home pooja. Contact temple for priest arrangement"
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

    "abhishekam": {
        "name": "Abhishekam Items",
        "items": """• Milk (1-2 liters)
• Yogurt (1 cup)
• Honey (1 cup)
• Ghee (1/4 cup)
• Sugar or jaggery
• Panchamritham ingredients
• Sacred water
• Flowers for decoration
• Turmeric and kumkum""",
        "note": "Check weekly abhishekam schedule"
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

# ============================================================
# HARD-CODED TEMPLE INFO
# ============================================================

TEMPLE_INFO = {
    "address": "1495 South Ridge Road, Castle Rock, Colorado 80104",
    "phone": "303-898-5514",
    "temple_main": "303-660-9555",
    "email": "manager@svtempleco.org",
    "website": "www.svtempleco.org",
    
    # TEMPLE TIMINGS
    "hours": {
        "weekday": "Weekdays (Monday-Friday): 9:00 AM - 12:00 PM and 6:00 PM - 8:00 PM",
        "weekend": "Weekends and Holidays: 9:00 AM - 8:00 PM",
        "cafeteria": "Cafeteria: Weekends only (Saturday & Sunday) 12:00 PM - 2:00 PM"
    },
    
    # LEADERSHIP & COMMITTEES
    "contacts": {
        "chairman": "Saiganesh Rajamani - 303-941-4166",
        "president": "Sri. Satyanarayana Velagapudi (Executive Committee President)",
        "manager": "Sri. Nandu Sankaran - 303-898-5514 or manager@svtempleco.org",
        "catering": "Annapoorna Committee Chair Smt. Swetha Sarvabhotla - 537-462-6167"
    },
    
    # TEMPLE COMMITTEES
    "committees": {
        "annapoorna": "Annapoorna Committee - Smt. Swetha Sarvabhotla (Chair) - 537-462-6167",
        "religious": "Religious Committee - Sri. Raju Dandu (Chair)",
        "finance": "Finance Committee - Sri. Dileep Kumar Kadirimangalam (Chair)",
        "executive": "Executive Committee - Sri. Satyanarayana Velagapudi (President)",
        "web_communications": "Web & Communications Committee - Smt. Suneeja Ankana (Chair)",
        "multimedia": "Multi Media Committee - Sri. Srinivasa Katamaneni (Chair)",
        "facilities": "Facilities Committee - Sri. Balu Gullepalli (Chair)",
        "education_cultural": "Education & Cultural Committee - Sri. Krishna Madhavan (Chair)",
        "security": "Security Committee - Sri. Muthukumarappan Ramurthy (Chair)"
    }
}

# ============================================================
# DAILY & MONTHLY SCHEDULE
# ============================================================

DAILY_SCHEDULE = [
    "09:00 AM – Sri Venkateswara Suprabhata Seva",
    "10:00 AM – Sri Venkateswara Nitya Archana"
]

MONTHLY_SCHEDULE = [
    "Full Moon Day – 06:30 PM – Sri Satyanarayana Swamy Pooja and Vratam"
]

# ============================================================
# WEEKLY ABHISHEKAM SCHEDULE (EXACT FROM TEMPLE)
# ============================================================

WEEKLY_EVENTS = {
    # Week 1
    "venkateswara swamy abhishekam": "1ST WEEK - Saturday 11:00 AM – Sri Venkateswara Swamy Abhishekam (Moola Murthy)",
    "venkateswara abhishekam": "1ST WEEK - Saturday 11:00 AM – Sri Venkateswara Swamy Abhishekam (Moola Murthy)",
    "1st saturday": "11:00 AM – Sri Venkateswara Swamy Abhishekam (Moola Murthy)",
    "first saturday": "11:00 AM – Sri Venkateswara Swamy Abhishekam (Moola Murthy)",
    
    "siva abhishekam": "1ST WEEK - Sunday 11:00 AM – Sri Siva Abhishekam",
    "shiva abhishekam": "1ST WEEK - Sunday 11:00 AM – Sri Siva Abhishekam",
    "1st sunday": "11:00 AM – Sri Siva Abhishekam",
    "first sunday": "11:00 AM – Sri Siva Abhishekam",
    
    # Week 2
    "venkateswara swamy kalyanam": "2ND WEEK - Saturday 11:00 AM – Sri Venkateswara Swamy Kalyanam",
    "kalyanam": "2ND WEEK - Saturday 11:00 AM – Sri Venkateswara Swamy Kalyanam",
    "2nd saturday": "11:00 AM – Sri Venkateswara Swamy Kalyanam",
    "second saturday": "11:00 AM – Sri Venkateswara Swamy Kalyanam",
    
    "vijaya ganapati": "2ND WEEK - Sunday 11:00 AM – Sri Vijaya Ganapati and Sri Valli Devasena Sahitha Murugan Abhishekam",
    "ganapati abhishekam": "2ND WEEK - Sunday 11:00 AM – Sri Vijaya Ganapati and Sri Valli Devasena Sahitha Murugan Abhishekam",
    "murugan abhishekam": "2ND WEEK - Sunday 11:00 AM – Sri Vijaya Ganapati and Sri Valli Devasena Sahitha Murugan Abhishekam",
    "2nd sunday": "11:00 AM – Sri Vijaya Ganapati and Sri Valli Devasena Sahitha Murugan Abhishekam",
    "second sunday": "11:00 AM – Sri Vijaya Ganapati and Sri Valli Devasena Sahitha Murugan Abhishekam",
    
    # Week 3
    "andal abhishekam": "3RD WEEK - Friday 11:00 AM – Sri Andal Abhishekam (Moola Murthy)",
    "3rd friday": "11:00 AM – Sri Andal Abhishekam (Moola Murthy)",
    "third friday": "11:00 AM – Sri Andal Abhishekam (Moola Murthy)",
    
    "mahalakshmi abhishekam": "3RD WEEK - Saturday 11:00 AM – Sri Mahalakshmi Abhishekam (Moola Murthy)",
    "3rd saturday": "11:00 AM – Sri Mahalakshmi Abhishekam (Moola Murthy)",
    "third saturday": "11:00 AM – Sri Mahalakshmi Abhishekam (Moola Murthy)",
    
    "shirdi sai baba": "3RD WEEK - Sunday 11:00 AM – Sri Shirdi Sai Baba and Sri Raghavendra Swamy Abhishekam",
    "sai baba abhishekam": "3RD WEEK - Sunday 11:00 AM – Sri Shirdi Sai Baba and Sri Raghavendra Swamy Abhishekam",
    "raghavendra swamy abhishekam": "3RD WEEK - Sunday 11:00 AM – Sri Shirdi Sai Baba and Sri Raghavendra Swamy Abhishekam",
    "raghavendra abhishekam": "3RD WEEK - Sunday 11:00 AM – Sri Shirdi Sai Baba and Sri Raghavendra Swamy Abhishekam",
    "3rd sunday": "11:00 AM – Sri Shirdi Sai Baba and Sri Raghavendra Swamy Abhishekam",
    "third sunday": "11:00 AM – Sri Shirdi Sai Baba and Sri Raghavendra Swamy Abhishekam",
    
    # Week 4
    "hanuman abhishekam": "4TH WEEK - Saturday 11:00 AM – Sri Hanuman Abhishekam",
    "4th saturday": "11:00 AM – Sri Hanuman Abhishekam",
    "fourth saturday": "11:00 AM – Sri Hanuman Abhishekam",
    
    "sudarshana homam": "4TH WEEK - Sunday 11:00 AM – Sri Sudarshana Homam",
    "4th sunday": "11:00 AM – Sri Sudarshana Homam",
    "fourth sunday": "11:00 AM – Sri Sudarshana Homam"
}

# ============================================================
# COMMON INSTRUCTIONS
# ============================================================

INSTRUCTIONS = {
    "vahana_pooja": "Walk-ins are welcome subject to availability of priest. Bring: lemons, 1 coconut, fruits and flowers",
    "schedule_pooja": "Contact manager at 303-898-5514 or email manager@svtempleco.org",
    "vastram_sponsor": "Contact manager at 303-898-5514 or email manager@svtempleco.org"
}

# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def _is_weekend(now: datetime) -> bool:
    """Check if today is weekend (Saturday=5, Sunday=6)"""
    return now.weekday() in [5, 6]

def _sanitize(text: str) -> str:
    """Clean up text and remove thinking tags"""
    if not isinstance(text, str):
        text = str(text)
    
    # Remove thinking/reasoning tags
    patterns = [
        r"(?is)<think>.*?</think>",
        r"(?is)```(?:thinking|reasoning|thoughts).*?```",
    ]
    for pat in patterns:
        text = re.sub(pat, "", text, flags=re.DOTALL | re.IGNORECASE)
    
    return text.strip()

# ============================================================
# FORMAT RAG RESULTS
# ============================================================

def _format_bullets(raw: str) -> str:
    """Simple bullet point formatting"""
    if not raw or not raw.strip():
        return ""
    
    lines = [l.strip() for l in raw.split("\n") if l.strip()]
    formatted = []
    
    for line in lines:
        # Skip if already has bullet
        if line.startswith(("•", "-", "*")):
            formatted.append(line)
        else:
            formatted.append(f"• {line}")
    
    return "\n".join(formatted)

# ============================================================
# MAIN ANSWER FUNCTION
# ============================================================

def answer_user(question: str) -> str:
    """
    Main function to answer user questions.
    Priority: Hardcoded responses > RAG search
    """
    q = (question or "").lower()
    now = datetime.now(ZoneInfo("America/Denver"))
    ts = now.strftime("%B %d, %Y %I:%M %p %Z")
    out = None

    # --------------------------------------------------------
    # 1. TEMPLE HOURS & TIMINGS
    # --------------------------------------------------------
    if any(word in q for word in ["open", "close", "timing", "hours"]):
        if "cafeteria" in q:
            out = f"• {TEMPLE_INFO['hours']['cafeteria']}"
        elif "today" in q:
            if _is_weekend(now):
                out = f"• Yes, temple is open today.\n• {TEMPLE_INFO['hours']['weekend']}"
            else:
                out = f"• Yes, temple is open today.\n• {TEMPLE_INFO['hours']['weekday']}"
        else:
            out = (
                f"• {TEMPLE_INFO['hours']['weekday']}\n"
                f"• {TEMPLE_INFO['hours']['weekend']}\n"
                f"• {TEMPLE_INFO['hours']['cafeteria']}"
            )

    # --------------------------------------------------------
    # 2. ADDRESS & LOCATION
    # --------------------------------------------------------
    elif "address" in q or "location" in q or "where is" in q:
        out = (
            f"• Address: {TEMPLE_INFO['address']}\n"
            f"• Website: {TEMPLE_INFO['website']}"
        )

    # --------------------------------------------------------
    # 3. CONVERSATIONAL: "What's happening today/at temple?"
    # --------------------------------------------------------
    if out is None and any(phrase in q for phrase in [
        "what's happening", "whats happening", "happening today", 
        "happening at temple", "any event", "events today",
        "what is today", "today's event", "todays event",
        "temple today", "going on today"
    ]):
        # Get today's information
        today_info = []
        
        # 1. Check if temple is open
        if _is_weekend(now):
            today_info.append("🏛️ Temple is open today (9:00 AM - 8:00 PM)")
        else:
            today_info.append("🏛️ Temple is open today (9:00 AM - 12:00 PM, 6:00 PM - 8:00 PM)")
        
        # 2. Add daily schedule
        today_info.append("\n📿 DAILY SCHEDULE:")
        for schedule_item in DAILY_SCHEDULE:
            today_info.append(f"• {schedule_item}")
        
        # 3. Check for today's panchang/events
        current_month = now.strftime("%B").lower()
        current_day = now.day
        month_abbr = now.strftime("%b")
        search_pattern = f"{month_abbr} {current_day}"
        
        # Try to find today's events from panchang
        panchang_files = [
            os.path.join("data_raw", f"{current_month}_panchang.txt"),
            os.path.join("data_raw", "Panchang", f"{current_month}_panchang.txt"),
        ]
        
        for panchang_file in panchang_files:
            if os.path.exists(panchang_file):
                try:
                    with open(panchang_file, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                    
                    for i, line in enumerate(lines):
                        if line.strip().startswith(search_pattern):
                            # Found today's panchang
                            today_info.append(f"\n🌙 TODAY'S PANCHANG:")
                            today_info.append(f"• {line.strip()}")
                            
                            # Check for event
                            if i + 1 < len(lines):
                                next_line = lines[i + 1].strip()
                                if next_line.startswith("Event:") and "None" not in next_line:
                                    event_text = next_line.replace("Event:", "").strip()
                                    today_info.append(f"\n🎉 SPECIAL EVENT TODAY:")
                                    today_info.append(f"• {event_text}")
                            break
                    break
                except:
                    pass
        
        # 4. Check if today is abhishekam day
        day_of_week = now.strftime("%A").lower()
        week_of_month = (now.day - 1) // 7 + 1
        
        for key, schedule in WEEKLY_EVENTS.items():
            if any(keyword in key for keyword in [f"{week_of_month}st", f"{week_of_month}nd", f"{week_of_month}rd", f"{week_of_month}th"]):
                if day_of_week in key:
                    today_info.append(f"\n🪔 ABHISHEKAM TODAY:")
                    today_info.append(f"• {schedule}")
        
        out = "\n".join(today_info)

    # --------------------------------------------------------
    # 4. CONTACT INFORMATION
    # --------------------------------------------------------
    elif any(word in q for word in ["phone", "contact", "call", "email", "number"]):
        if "chairman" in q:
            out = f"• Chairman: {TEMPLE_INFO['contacts']['chairman']}"
        elif "president" in q:
            out = f"• President: {TEMPLE_INFO['contacts']['president']}"
        elif "manager" in q:
            out = f"• Manager: {TEMPLE_INFO['contacts']['manager']}"
        elif "catering" in q or "annapoorna" in q:
            out = f"• Catering: {TEMPLE_INFO['contacts']['catering']}"
        else:
            out = (
                f"• Temple: {TEMPLE_INFO['temple_main']}\n"
                f"• Manager: {TEMPLE_INFO['phone']}\n"
                f"• Email: {TEMPLE_INFO['email']}"
            )

    # --------------------------------------------------------
    # 4. VAHANA POOJA
    # --------------------------------------------------------
    elif "vahana" in q or "car pooja" in q:
        out = f"• {INSTRUCTIONS['vahana_pooja']}"

    # --------------------------------------------------------
    # 5. COMMITTEE & LEADERSHIP CONTACTS
    # --------------------------------------------------------
    if out is None and any(word in q for word in ["committee", "chair", "chairperson", "leadership", "board"]):
        
        # Specific committee queries
        if any(word in q for word in ["catering", "food", "annapurna", "annapoorna"]):
            out = f"• {TEMPLE_INFO['committees']['annapoorna']}\n• For catering services, contact: Smt. Swetha Sarvabhotla at 537-462-6167"
        
        elif any(word in q for word in ["religious", "pooja", "ritual"]):
            out = f"• {TEMPLE_INFO['committees']['religious']}"
        
        elif any(word in q for word in ["finance", "donation", "money"]):
            out = f"• {TEMPLE_INFO['committees']['finance']}"
        
        elif any(word in q for word in ["web", "website", "communication"]):
            out = f"• {TEMPLE_INFO['committees']['web_communications']}"
        
        elif any(word in q for word in ["multimedia", "media", "video", "audio"]):
            out = f"• {TEMPLE_INFO['committees']['multimedia']}"
        
        elif any(word in q for word in ["facility", "facilities", "maintenance", "building"]):
            out = f"• {TEMPLE_INFO['committees']['facilities']}"
        
        elif any(word in q for word in ["education", "cultural", "class", "event"]):
            out = f"• {TEMPLE_INFO['committees']['education_cultural']}"
        
        elif any(word in q for word in ["security", "safety"]):
            out = f"• {TEMPLE_INFO['committees']['security']}"
        
        elif any(word in q for word in ["executive", "president"]):
            out = f"• {TEMPLE_INFO['committees']['executive']}"
        
        elif "all" in q or "list" in q:
            # List all committees
            out = "TEMPLE COMMITTEES:\n\n"
            out += f"• Chairman: {TEMPLE_INFO['contacts']['chairman']}\n"
            out += f"• {TEMPLE_INFO['contacts']['president']}\n"
            out += f"• Temple Manager: {TEMPLE_INFO['contacts']['manager']}\n\n"
            out += "COMMITTEES:\n"
            for committee_info in TEMPLE_INFO['committees'].values():
                out += f"• {committee_info}\n"

    # --------------------------------------------------------
    # 6. SCHEDULING / BOOKING
    # --------------------------------------------------------
    elif any(word in q for word in ["schedule", "book", "appointment", "sponsor"]):
        if "vastram" in q:
            out = f"• Vastram Sponsorship: {INSTRUCTIONS['vastram_sponsor']}"
        else:
            out = f"• To schedule a pooja: {INSTRUCTIONS['schedule_pooja']}"

    # --------------------------------------------------------
    # 6. DAILY SCHEDULE
    # --------------------------------------------------------
    elif "daily" in q and ("pooja" in q or "schedule" in q):
        out = "Daily Temple Schedule:\n" + "\n".join(f"• {s}" for s in DAILY_SCHEDULE)

    # --------------------------------------------------------
    # 7. MONTHLY SCHEDULE
    # --------------------------------------------------------
    elif "monthly" in q and ("pooja" in q or "schedule" in q):
        out = "Monthly Schedule:\n" + "\n".join(f"• {s}" for s in MONTHLY_SCHEDULE)

    # --------------------------------------------------------
    # 7. ITEMS REQUIRED FOR POOJAS
    # --------------------------------------------------------
    if out is None and any(word in q for word in ["item", "bring", "need", "required", "material", "samagri"]):
        # Detect which type of pooja
        pooja_type = None
        
        if any(word in q for word in ["vahana", "vehicle", "car", "bike"]):
            pooja_type = "vahana"
        elif any(word in q for word in ["satyanarayana", "satyanarayan", "vratam"]):
            # Determine if at temple or home
            if any(word in q for word in ["home", "house"]):
                pooja_type = "satyanarayana_home"
            else:
                pooja_type = "satyanarayana_temple"
        elif any(word in q for word in ["gruhapravesam", "gruha pravesam", "housewarming", "house warming", "new home"]):
            pooja_type = "gruhapravesam"
        elif any(word in q for word in ["vastu", "vastu shanti"]):
            pooja_type = "vastu"
        elif any(word in q for word in ["nischitartham", "nischitartha", "engagement", "betrothal"]):
            pooja_type = "nischitartham"
        elif any(word in q for word in ["hindu wedding", "wedding ceremony", "marriage ceremony", "vivaha"]):
            pooja_type = "hindu_wedding"
        elif any(word in q for word in ["hiranya", "sharddham", "shraddha", "shradh"]):
            pooja_type = "hiranya_sharddham"
        elif any(word in q for word in ["nava graha", "navagraha", "nine planet", "planetary"]):
            pooja_type = "nava_graha"
        elif any(word in q for word in ["aksharabhyasam", "akshara abhyasam", "vidyarambham", "vidya arambham", "first writing"]):
            pooja_type = "aksharabhyasam"
        elif any(word in q for word in ["half saree", "halfsaree", "ritu kala"]):
            pooja_type = "half_saree"
        elif any(word in q for word in ["any homam", "general homam"]):
            pooja_type = "any_homam"
        elif any(word in q for word in ["homam", "homa", "havan", "fire"]):
            pooja_type = "homam"
        elif any(word in q for word in ["abhishekam", "abhisheka"]):
            pooja_type = "abhishekam"
        elif any(word in q for word in ["archana", "archan"]):
            pooja_type = "archana"
        elif any(word in q for word in ["kalyanam", "kalyan", "wedding", "marriage", "venkateswara kalyanam"]):
            pooja_type = "kalyanam"
        elif any(word in q for word in ["bhoomi", "bhoomi pooja", "foundation"]):
            pooja_type = "bhoomi_pooja"
        elif any(word in q for word in ["annaprasana", "anna prasana", "first rice"]):
            pooja_type = "annaprasana"
        elif any(word in q for word in ["namakaranam", "nama karanam", "naming ceremony"]):
            pooja_type = "namakaranam"
        elif any(word in q for word in ["hair offering", "mundan", "shave", "tonsure"]):
            pooja_type = "hair_offering"
        elif any(word in q for word in ["seemantham", "seemantha", "baby shower"]):
            pooja_type = "seemantham"
        elif any(word in q for word in ["sudarshana", "sudarsana"]):
            pooja_type = "sudarshana"
        else:
            pooja_type = "general"
        
        # Get items for the pooja type
        if pooja_type and pooja_type in ITEMS_REQUIRED:
            pooja_info = ITEMS_REQUIRED[pooja_type]
            
            out = f"{pooja_info['name'].upper()}:\n\n"
            out += pooja_info['items']
            out += f"\n\n📌 {pooja_info['note']}"
            out += f"\n\n🔗 Complete list: {POOJA_SAMAGRI_URL}"
            out += "\n📞 Contact: 303-898-5514"

    # --------------------------------------------------------
    # 8. PANCHANG & DATE QUERIES
    # --------------------------------------------------------
    # Only trigger if query is actually asking about panchang/dates
    is_panchang_query = (
        any(word in q for word in ["panchang", "tithi", "nakshatra"]) or
        any(phrase in q for phrase in ["what's happening", "whats happening", "happening today", "happening at temple", "events today", "today's event"]) or
        (any(word in q for word in ["today", "tomorrow"]) and any(word in q for word in ["panchang", "tithi", "nakshatra", "event", "special", "auspicious"])) or
        any(month in q for month in ["dec", "jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov"]) and any(word in q for word in ["purnima", "amavasya", "ekadasi", "full moon", "new moon"])
    )
    
    if out is None and is_panchang_query:
        
        # Detect if asking about today or a specific date
        is_today_query = any(phrase in q for phrase in ["today", "today's", "todays", "current"])
        
        # Try to extract specific date from query (e.g., "Dec 1", "December 1st")
        target_date = None
        target_month = None
        target_day = None
        
        # Check for specific date patterns
        date_patterns = [
            (r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+(\d+)', 'abbr'),  # "Dec 1" or "December 1st"
        ]
        
        for pattern, format_type in date_patterns:
            match = re.search(pattern, q, re.IGNORECASE)
            if match:
                month_str = match.group(1).lower()
                day_str = match.group(2)
                
                # Map month abbreviation to full month name
                month_map = {
                    'jan': 'january', 'feb': 'february', 'mar': 'march', 'apr': 'april',
                    'may': 'may', 'jun': 'june', 'jul': 'july', 'aug': 'august',
                    'sep': 'september', 'oct': 'october', 'nov': 'november', 'dec': 'december'
                }
                
                target_month = month_map.get(month_str[:3])
                try:
                    target_day = int(day_str)
                    target_date = f"{month_str.capitalize()} {target_day}"
                except:
                    pass
                break
        
        # If no specific date mentioned, use today
        if not target_date and (is_today_query or any(word in q for word in ["panchang", "tithi", "nakshatra"])):
            target_month = now.strftime("%B").lower()
            target_day = now.day
            target_date = f"{now.strftime('%b')} {target_day}"
            date_label = f"Today's Panchang ({now.strftime('%B %d, %Y')})"
        else:
            date_label = f"Panchang for {target_date}"
        
        if target_month and target_day:
            # Get month abbreviation (e.g., "Dec" for December)
            month_abbr_map = {
                'january': 'Jan', 'february': 'Feb', 'march': 'Mar', 'april': 'Apr',
                'may': 'May', 'june': 'Jun', 'july': 'Jul', 'august': 'Aug',
                'september': 'Sep', 'october': 'Oct', 'november': 'Nov', 'december': 'Dec'
            }
            target_month_abbr = month_abbr_map.get(target_month, target_month[:3].capitalize())
            
            # Pattern to match: "Dec 1" or "Nov 30"
            search_pattern = f"{target_month_abbr} {target_day}"
            
            # Try to find panchang file for target month
            panchang_files = [
                os.path.join("data_raw", f"{target_month}_panchang.txt"),
                os.path.join("data_raw", "Panchang", f"{target_month}_panchang.txt"),  # Capital P
                os.path.join("data_raw", "panchang", f"{target_month}_panchang.txt"),
                f"{target_month}_panchang.txt"
            ]
            
            panchang_found = False
            
            for panchang_file in panchang_files:
                if os.path.exists(panchang_file):
                    try:
                        with open(panchang_file, "r", encoding="utf-8") as f:
                            lines = f.readlines()
                        
                        # Find the line with target date
                        for i, line in enumerate(lines):
                            line_stripped = line.strip()
                            
                            # Check if this line contains target date (e.g., "Dec 1")
                            if line_stripped.startswith(search_pattern):
                                # Found the panchang!
                                today_info = [line_stripped]
                                
                                # Check if next line has an Event
                                if i + 1 < len(lines):
                                    next_line = lines[i + 1].strip()
                                    if next_line.startswith("Event:") and next_line != "Event: None":
                                        today_info.append(next_line)
                                
                                out = f"{date_label}:\n" + "\n".join(f"• {l}" for l in today_info)
                                panchang_found = True
                                break
                        
                        if panchang_found:
                            break
                            
                    except Exception as e:
                        print(f"Error reading panchang file {panchang_file}: {e}")
                        continue
            
            # If still not found, provide helpful message
            if not panchang_found:
                if target_date:
                    out = (
                        f"• Panchang information for {target_date} is not available in the data files.\n"
                        f"• Please contact temple manager at 303-898-5514"
                    )
                else:
                    out = (
                        f"• Today is {now.strftime('%B %d, %Y')}\n"
                        f"• Panchang information for today is not available in the data files.\n"
                        f"• Please contact temple manager at 303-898-5514"
                    )

    # --------------------------------------------------------
    # 9. ABHISHEKAM SCHEDULES (only if asking "when")
    # --------------------------------------------------------
    if out is None and any(word in q for word in ["when", "what time", "schedule"]):
        for keyword, schedule in WEEKLY_EVENTS.items():
            if keyword in q or keyword.replace(" ", "") in q:
                out = f"• {schedule}"
                break

    # --------------------------------------------------------
    # 9. RAG SEARCH FOR EVERYTHING ELSE
    # --------------------------------------------------------
    if out is None:
        # Detect if user specified a month
        specified_month = None
        for month in ["january", "february", "march", "april", "may", "june", 
                     "july", "august", "september", "october", "november", "december"]:
            if month in q:
                specified_month = month
                break
        
        # If no month specified and query is about dates, use current month
        is_date_query = any(word in q for word in ["full moon", "purnima", "amavasya", "ekadasi", "ekadashi", "new moon"])
        if not specified_month and is_date_query:
            specified_month = now.strftime("%B").lower()
        
        try:
            # For "meaning" or "what is" queries, use more chunks and specific handling
            if any(word in q for word in ["meaning", "what is", "explain", "significance", "why", "about"]):
                k_value = 10  # More results for explanatory queries
            else:
                k_value = 7
            
            # Search for relevant information in indexed documents
            # This will search ALL .txt files in data_raw/ including rituals/*.txt
            chunks = get_chunks(question, k=k_value)
            
            if chunks:
                # Combine relevant text from chunks
                texts = []
                seen = set()  # Avoid duplicates
                
                # Month abbreviation mapping for filtering
                month_abbr_map = {
                    'january': 'Jan', 'february': 'Feb', 'march': 'Mar', 'april': 'Apr',
                    'may': 'May', 'june': 'Jun', 'july': 'Jul', 'august': 'Aug',
                    'september': 'Sep', 'october': 'Oct', 'november': 'Nov', 'december': 'Dec'
                }
                
                for chunk in chunks:
                    text = chunk.get("text", "").strip()
                    
                    # Skip very short fragments
                    if not text or len(text) < 20:
                        continue
                    
                    # For date queries, filter to specified month only
                    if is_date_query and specified_month:
                        target_abbr = month_abbr_map.get(specified_month, specified_month[:3].capitalize())
                        
                        # Only include if text mentions the target month
                        if target_abbr not in text and specified_month.capitalize() not in text:
                            continue
                    
                    # Skip duplicates
                    if text not in seen:
                        texts.append(text)
                        seen.add(text)
                
                if texts:
                    # For meaning/explanation queries, use more content
                    if any(word in q for word in ["meaning", "what is", "explain", "significance", "why"]):
                        context = "\n".join(texts[:7])  # Top 7 for detailed answers
                    else:
                        context = "\n".join(texts[:5])  # Top 5 for regular queries
                    
                    # Use LLM to generate natural conversational response
                    try:
                        prompt = f"""You are a helpful assistant for Sri Venkateswara Temple in Castle Rock, Colorado.
Based on the following information from temple documents, please answer the user's question naturally and conversationally.

Temple Information:
{context}

User Question: {question}

Instructions:
- Answer naturally and conversationally in a friendly tone
- Use ONLY the information provided above from temple documents
- If the information doesn't fully answer the question, provide what you can and mention contacting the temple for more details
- Keep response concise (3-5 sentences for simple queries, more for complex questions)
- Include relevant details from the temple information
- For dates/schedules, be specific with the information provided
- Do not make up information not present in the temple documents

Answer:"""

                        # Call AWS Bedrock Claude
                        response = bedrock_runtime.invoke_model(
                            modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
                            body=json.dumps({
                                "anthropic_version": "bedrock-2023-05-31",
                                "max_tokens": 500,
                                "temperature": 0.3,
                                "messages": [{
                                    "role": "user",
                                    "content": prompt
                                }]
                            })
                        )
                        
                        # Extract LLM response
                        result = json.loads(response['body'].read())
                        llm_answer = result['content'][0]['text'].strip()
                        
                        out = llm_answer
                        
                    except Exception as llm_error:
                        print(f"LLM generation error: {llm_error}")
                        # Fallback to raw chunks if LLM fails
                        out = _format_bullets(context)
        
        except Exception as e:
            print(f"RAG search error: {e}")
            # Continue to fallback
    
    # --------------------------------------------------------
    # 10. FALLBACK MESSAGE
    # --------------------------------------------------------
    if not out or not out.strip():
        out = (
            "• I don't have specific information about that right now.\n"
            f"• Please contact the temple manager:\n"
            f"• Phone: {TEMPLE_INFO['phone']}\n"
            f"• Email: {TEMPLE_INFO['email']}"
        )

    # --------------------------------------------------------
    # FINAL FORMATTED RESPONSE
    # --------------------------------------------------------
    return (
        f"{ts}\n"
        f"Om Namo Venkateshaya Namah\n\n"
        f"{out}\n\n"
        f"Thank you. Om Namo Venkateshaya!"
    )