#!/usr/bin/env python3
"""
Comprehensive Test Suite for SV Temple WhatsApp Bot
Tests all features: poojas, schedules, contacts, panchang, items, LLM responses
"""

import sys
import os

# Add the backend directory to path for imports
# Assumes test file is in project root, backend/ is a subdirectory
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(current_dir, 'backend')
sys.path.insert(0, backend_dir)
sys.path.insert(0, current_dir)

# Try multiple import methods
try:
    from backend.ask_temple import answer_user
    print("✅ Successfully imported from backend.ask_temple")
except ImportError:
    try:
        from ask_temple import answer_user
        print("✅ Successfully imported from ask_temple")
    except ImportError:
        print("⚠️  WARNING: Could not import ask_temple module!")
        print("⚠️  Running in MOCK MODE (showing test structure only)")
        print("⚠️  To run real tests:")
        print("⚠️  1. Place this file in project root: C:\\My_Projects\\sv-temple-assistant\\")
        print("⚠️  2. Ensure backend/ask_temple.py exists")
        print("⚠️  3. Run: python comprehensive_test_suite.py")
        print()
        def answer_user(query):
            return f"[MOCK RESPONSE for: {query}]"

def print_test(test_name, query, expected_keywords=None):
    """Helper function to print test results"""
    print("\n" + "=" * 80)
    print(f"TEST: {test_name}")
    print("=" * 80)
    print(f"Query: '{query}'")
    print("-" * 80)
    
    try:
        response = answer_user(query)
        print(response)
        
        # Check for expected keywords if provided
        if expected_keywords:
            print("\n" + "-" * 80)
            print("✅ CHECKING FOR EXPECTED KEYWORDS:")
            for keyword in expected_keywords:
                if keyword.lower() in response.lower():
                    print(f"  ✅ Found: '{keyword}'")
                else:
                    print(f"  ❌ Missing: '{keyword}'")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print("=" * 80)

def main():
    print("\n" + "🕉" * 40)
    print("SRI VENKATESWARA TEMPLE BOT - COMPREHENSIVE TEST SUITE")
    print("🕉" * 40)
    
    # =================================================================
    # CATEGORY 1: TEMPLE EVENTS & HAPPENINGS
    # =================================================================
    print("\n\n" + "📅" * 40)
    print("CATEGORY 1: TEMPLE EVENTS & HAPPENINGS")
    print("📅" * 40)
    
    print_test(
        "1.1 - Events happening today",
        "what's happening today at temple",
        ["Temple is open", "DAILY SCHEDULE", "Suprabhata Seva", "Nitya Archana", "PANCHANG"]
    )
    
    print_test(
        "1.2 - Current month events",
        "what are the events this month",
        ["December", "Margasira", "Ekadasi", "Full Moon"]
    )
    
    print_test(
        "1.3 - Today's events (alternative)",
        "any events today",
        ["Temple is open", "DAILY SCHEDULE"]
    )
    
    # =================================================================
    # CATEGORY 2: ABHISHEKAM SCHEDULE
    # =================================================================
    print("\n\n" + "🪔" * 40)
    print("CATEGORY 2: ABHISHEKAM SCHEDULE")
    print("🪔" * 40)
    
    print_test(
        "2.1 - When is abhishekam",
        "when is abhishekam",
        ["WEEK", "Saturday", "Sunday", "11:00 AM", "Venkateswara", "Siva"]
    )
    
    print_test(
        "2.2 - Abhishekam schedule",
        "abhishekam schedule",
        ["1ST WEEK", "2ND WEEK", "3RD WEEK", "4TH WEEK"]
    )
    
    print_test(
        "2.3 - Venkateswara abhishekam",
        "when is venkateswara swamy abhishekam",
        ["1ST WEEK", "Saturday", "11:00 AM"]
    )
    
    # =================================================================
    # CATEGORY 3: DAILY POOJA & TEMPLE TIMINGS
    # =================================================================
    print("\n\n" + "⏰" * 40)
    print("CATEGORY 3: DAILY POOJA & TEMPLE TIMINGS")
    print("⏰" * 40)
    
    print_test(
        "3.1 - Daily pooja schedule",
        "daily pooja timings",
        ["Suprabhata Seva", "Nitya Archana", "9:00 AM", "10:00 AM"]
    )
    
    print_test(
        "3.2 - Temple timings",
        "temple hours",
        ["Weekdays", "Weekends", "9:00 AM", "8:00 PM"]
    )
    
    print_test(
        "3.3 - Is temple open today",
        "is temple open today",
        ["Temple is open", "9:00 AM"]
    )
    
    # =================================================================
    # CATEGORY 4: TEMPLE LOCATION & FACILITIES
    # =================================================================
    print("\n\n" + "📍" * 40)
    print("CATEGORY 4: TEMPLE LOCATION & FACILITIES")
    print("📍" * 40)
    
    print_test(
        "4.1 - Temple location",
        "temple location",
        ["Castle Rock", "Colorado", "address"]
    )
    
    print_test(
        "4.2 - Is cafeteria open today",
        "is cafeteria open today",
        ["Annapoorna", "cafeteria", "contact"]
    )
    
    print_test(
        "4.3 - Temple address",
        "what is temple address",
        ["Castle Rock", "80104"]
    )
    
    # =================================================================
    # CATEGORY 5: CONTACTS & LEADERSHIP
    # =================================================================
    print("\n\n" + "📞" * 40)
    print("CATEGORY 5: CONTACTS & LEADERSHIP")
    print("📞" * 40)
    
    print_test(
        "5.1 - Annapoorna committee contact",
        "annapoorna committee contact",
        ["Annapoorna", "Swetha Sarvabhotla", "537-462-6167"]
    )
    
    print_test(
        "5.2 - Who is chairman",
        "who is the chairman",
        ["President", "Chairman", "LEADERSHIP"]
    )
    
    print_test(
        "5.3 - Temple manager contact",
        "contact temple manager",
        ["303-898-5514", "manager@svtempleco.org"]
    )
    
    print_test(
        "5.4 - Catering contact",
        "contact for catering",
        ["Annapoorna", "Swetha"]
    )
    
    # =================================================================
    # CATEGORY 6: PANCHANG QUERIES
    # =================================================================
    print("\n\n" + "🌙" * 40)
    print("CATEGORY 6: PANCHANG QUERIES")
    print("🌙" * 40)
    
    print_test(
        "6.1 - Full moon day in current month",
        "full moon day in December",
        ["Purnima", "Full Moon", "December", "Dec"]
    )
    
    print_test(
        "6.2 - Amavasya in current month",
        "amavasya in December",
        ["Amavasya", "New Moon", "December", "Dec"]
    )
    
    print_test(
        "6.3 - Today's panchang",
        "today's panchang",
        ["Tithi", "Nakshatra", "Panchang"]
    )
    
    print_test(
        "6.4 - Today's tithi",
        "what is today's tithi",
        ["Tithi", "Panchang"]
    )
    
    print_test(
        "6.5 - Specific date panchang",
        "panchang for Dec 15",
        ["Dec 15", "Tithi", "Nakshatra"]
    )
    
    print_test(
        "6.6 - Ekadasi in December",
        "when is ekadasi in December",
        ["Ekadasi", "December", "Dec"]
    )
    
    # =================================================================
    # CATEGORY 7: POOJA COSTS & SEVA PRICES
    # =================================================================
    print("\n\n" + "💰" * 40)
    print("CATEGORY 7: POOJA COSTS & SEVA PRICES")
    print("💰" * 40)
    
    print_test(
        "7.1 - Seva cost",
        "what is the seva cost",
        ["seva", "cost", "contact", "303-898-5514"]
    )
    
    print_test(
        "7.2 - Homam cost",
        "how much does homam cost",
        ["homam", "cost", "contact"]
    )
    
    print_test(
        "7.3 - Abhishekam cost",
        "abhishekam price",
        ["abhishekam", "cost", "contact"]
    )
    
    print_test(
        "7.4 - General pooja cost",
        "pooja costs",
        ["contact", "303-898-5514"]
    )
    
    # =================================================================
    # CATEGORY 8: MONTHLY POOJAS & SCHEDULE
    # =================================================================
    print("\n\n" + "📆" * 40)
    print("CATEGORY 8: MONTHLY POOJAS & SCHEDULE")
    print("📆" * 40)
    
    print_test(
        "8.1 - Monthly poojas at temple",
        "what are the monthly poojas",
        ["WEEK", "abhishekam", "Kalyanam", "Homam"]
    )
    
    print_test(
        "8.2 - Weekly abhishekam schedule",
        "weekly abhishekam",
        ["1ST WEEK", "2ND WEEK", "3RD WEEK", "4TH WEEK"]
    )
    
    print_test(
        "8.3 - Kalyanam schedule",
        "when is kalyanam",
        ["2ND WEEK", "Saturday", "Kalyanam"]
    )
    
    # =================================================================
    # CATEGORY 9: ITEMS REQUIRED FOR POOJAS
    # =================================================================
    print("\n\n" + "🛍️" * 40)
    print("CATEGORY 9: ITEMS REQUIRED FOR POOJAS")
    print("🛍️" * 40)
    
    print_test(
        "9.1 - Items for housewarming",
        "items required for gruhapravesam",
        ["GRUHAPRAVESAM", "Turmeric", "Kumkum", "Coconut", "42", "303-898-5514"]
    )
    
    print_test(
        "9.2 - Items for Satyanarayana pooja",
        "items for satyanarayana vratam",
        ["SATYANARAYANA", "Flowers", "Coconut", "Milk", "303-898-5514"]
    )
    
    print_test(
        "9.3 - Items for engagement",
        "items for engagement",
        ["NISCHITARTHAM", "ENGAGEMENT", "Turmeric", "Kumkum", "28"]
    )
    
    print_test(
        "9.4 - Items for wedding",
        "items for hindu wedding",
        ["WEDDING", "Mangalyam", "Rice", "20 Lbs", "40"]
    )
    
    print_test(
        "9.5 - Items for homam",
        "items for homam",
        ["HOMAM", "Dry coconuts", "Ghee", "Navadhanyam"]
    )
    
    print_test(
        "9.6 - Items for baby naming",
        "items for namakaranam",
        ["NAMAKARANAM", "NAMING", "Honey", "Milk"]
    )
    
    print_test(
        "9.7 - Items for aksharabhyasam",
        "items for aksharabhyasam",
        ["AKSHARABHYASAM", "Slate", "Chalk", "Notebook", "Pen"]
    )
    
    print_test(
        "9.8 - Items for half saree function",
        "items for half saree",
        ["HALF SAREE", "Kalasam", "Half saree"]
    )
    
    # =================================================================
    # CATEGORY 10: HINDU RITUALS MEANING (LLM POWERED)
    # =================================================================
    print("\n\n" + "📚" * 40)
    print("CATEGORY 10: HINDU RITUALS MEANING (LLM-POWERED)")
    print("📚" * 40)
    
    print_test(
        "10.1 - Meaning of Ekadasi",
        "what is the significance of Ekadasi",
        ["Ekadasi", "spiritual", "fasting"]
    )
    
    print_test(
        "10.2 - Explain Margashirsha month",
        "tell me about Margashirsha month",
        ["Margashirsha", "sacred", "month"]
    )
    
    print_test(
        "10.3 - Why Satyanarayana vratam",
        "why do we do Satyanarayana vratam",
        ["Satyanarayana", "vratam", "blessings"]
    )
    
    print_test(
        "10.4 - Meaning of Purnima",
        "what is the meaning of Purnima",
        ["Purnima", "Full Moon", "auspicious"]
    )
    
    print_test(
        "10.5 - Abhishekam significance",
        "what happens during abhishekam",
        ["abhishekam", "ritual", "deity"]
    )
    
    # =================================================================
    # CATEGORY 11: FESTIVAL EXPLANATIONS (LLM POWERED)
    # =================================================================
    print("\n\n" + "🎉" * 40)
    print("CATEGORY 11: FESTIVAL EXPLANATIONS (LLM-POWERED)")
    print("🎉" * 40)
    
    print_test(
        "11.1 - Dhanurmasam explanation",
        "tell me about Dhanurmasam",
        ["Dhanurmasam", "month", "Vishnu"]
    )
    
    print_test(
        "11.2 - Vaikunta Ekadasi",
        "what is Vaikunta Ekadasi",
        ["Vaikunta", "Ekadasi", "special"]
    )
    
    print_test(
        "11.3 - Brahmotsavam explanation",
        "explain Brahmotsavam",
        ["Brahmotsavam", "festival", "temple"]
    )
    
    # =================================================================
    # CATEGORY 12: NON-TEMPLE QUERIES (FALLBACK BEHAVIOR)
    # =================================================================
    print("\n\n" + "🚫" * 40)
    print("CATEGORY 12: NON-TEMPLE QUERIES (FALLBACK BEHAVIOR)")
    print("🚫" * 40)
    
    print_test(
        "12.1 - Weather query",
        "what's the weather today",
        ["don't have specific information", "contact", "temple manager", "303-898-5514"]
    )
    
    print_test(
        "12.2 - General knowledge",
        "who is the president of USA",
        ["don't have specific information", "contact", "303-898-5514"]
    )
    
    print_test(
        "12.3 - Cooking recipe",
        "how do I make pasta",
        ["don't have specific information", "contact"]
    )
    
    print_test(
        "12.4 - Sports query",
        "who won the game yesterday",
        ["don't have specific information", "manager"]
    )
    
    print_test(
        "12.5 - Movie recommendation",
        "what movies should I watch",
        ["don't have specific information", "contact"]
    )
    
    print_test(
        "12.6 - Restaurant query",
        "what's a good restaurant nearby",
        ["don't have", "contact", "temple"]
    )
    
    print_test(
        "12.7 - Personal question",
        "can you help me with my homework",
        ["don't have specific information"]
    )
    
    print_test(
        "12.8 - Chitchat",
        "how are you doing today",
        ["don't have", "contact"]
    )
    
    print_test(
        "12.9 - Random gibberish",
        "asdfghjkl qwerty",
        ["don't have specific information", "temple manager"]
    )
    
    print_test(
        "12.10 - News query",
        "what's in the news today",
        ["don't have", "contact", "303-898-5514"]
    )
    
    # =================================================================
    # SUMMARY
    # =================================================================
    print("\n\n" + "=" * 80)
    print("✅ TEST SUITE COMPLETE!")
    print("=" * 80)
    print("\nTEST CATEGORIES COVERED:")
    print("1. ✅ Temple Events & Happenings (3 tests)")
    print("2. ✅ Abhishekam Schedule (3 tests)")
    print("3. ✅ Daily Pooja & Temple Timings (3 tests)")
    print("4. ✅ Temple Location & Facilities (3 tests)")
    print("5. ✅ Contacts & Leadership (4 tests)")
    print("6. ✅ Panchang Queries (6 tests)")
    print("7. ✅ Pooja Costs & Seva Prices (4 tests)")
    print("8. ✅ Monthly Poojas & Schedule (3 tests)")
    print("9. ✅ Items Required for Poojas (8 tests)")
    print("10. ✅ Hindu Rituals Meaning - LLM (5 tests)")
    print("11. ✅ Festival Explanations - LLM (3 tests)")
    print("12. ✅ Non-Temple Queries - Fallback (10 tests)")
    print("\n📊 TOTAL: 55 COMPREHENSIVE TESTS")
    print("=" * 80)

if __name__ == "__main__":
    main()
