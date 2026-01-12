import logging
import pytest

from backend.ask_temple import answer_user

# ---------------------------------------------------------
# Logging setup
# ---------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------
# Fallback string (single source of truth)
# ---------------------------------------------------------
FALLBACK_RESPONSE = "• I don’t have specific information on that right now."

# ---------------------------------------------------------
# Test data: ALL user queries
# ---------------------------------------------------------
USER_QUERIES = [
    "Is the Temple Open Today (Holiday)?",
    "Aadi Krithigai",
    "Abhishekam sponsorship",
    "Address",
    "Adyayanotsavam",
    "Akshar Arambh",
    "Aksharabhyasam",
    "Aksharabhyasam items",
    "Amavasya dates",
    "Amma",
    "Ammavaru",
    "Andal Kalyanam",
    "Annadanam sponsorship",
    "Annadanam timing",
    "Annamacharya Day",
    "Annaprashana",
    "Antyeshti",
    "Any Special Events Today",
    "Appa",
    "Ashtami",
    "Avani Avittam",
    "Ayush Homam cost",
    "BalaVihar",
    "Beema Ratha Santhi",
    "Bhagavad Gita Class",
    "Bhajans at temple",
    "Bheeshma Ekadeshi",
    "Bhogi",
    "Bhoomi Puja",
    "Board of Trustees",
    "Brahmothsavam",
    "Cafeteria timing",
    "Calendar",
    "Catering contact",
    "Catering service contact",
    "Chaath Puja",
    "Chandi Homam",
    "Christmas",
    "Chudakarana",
    "Cloth offering to god",
    "Cultural Prograns",
    "Daily pooja schedule",
    "Dance performance at temple",
    "Dec 1 panchang",
    "Deepavali",
    "Diwali",
    "Diwali story",
    "Donate",
    "Durga Ashtami",
    "Dusshera",
    "Dwadhashi",
    "email",
    "English new year",
    "Events 2026",
    "Events January 2026",
    "Events Today",
    "Festival",
    "Festivals",
    "Founding Members",
    "Ganapathi Abisekam",
    "Ganesh Chathurthi",
    "Garbadhana",
    "Godha Kalyanam",
    "Gokulashtami",
    "Graha Puja",
    "Guru Purnima",
    "Hanuman Abisekam",
    "Hindu wedding pooja",
    "Holi",
    "Holiday",
    "Holiday hours",
    "How do I book a puja",
    "Is annadanam available today?",
    "Is the temple open today?",
    "Janmashtami",
    "Kanakabhisekam",
    "Karthigai Deepam",
    "Krishna Jayanthi",
    "Lakshmi Puja",
    "Lalitha Sahasranamam",
    "List arjitha sevas",
    "List of homams",
    "Maha Shivarathri",
    "Mahalakshmi Abhisekam",
    "Manager contact",
    "Martin Luther Day",
    "Meenakshi Kalyanam",
    "Monthly pooja schedule",
    "Murugan Abisekam",
    "Naalaayira Divya Prabhandham",
    "Nama Sankeerthanam",
    "Navagraha Puja",
    "Navarathri",
    "Nitya Archana",
    "Onam",
    "Pongal",
    "Pradhosham",
    "Ram Navami",
    "Rudrabhsekam",
    "Sahasranamam",
    "Satyanarayana pooja timing",
    "Shiva Abisekam",
    "Shivarathri",
    "Sri Venkateswra Temple of Colorado",
    "Subramanya Abisekam",
    "Suprabatham",
    "Tamil New year",
    "Temple address",
    "Temple Calendar",
    "Temple hours / timings",
    "Temple phone number",
    "Thanksgiving",
    "Today panchang",
    "Today's Events",
    "Tulsi Kalyanam",
    "Ugadi",
    "Upanayanam",
    "Vahana Puja",
    "Vaikunta Ekadesi",
    "Varalakshmi Vratham",
    "Venkateswara Abhisekam",
    "Venkateswara Kalyanam",
    "Vidyarambam",
    "Vijaya Dhashami",
    "Vinayakar Chathurthi",
    "Vishnu Sahasranamam",
    "Volunteer Appreciation",
    "Website",
    "Weekday hours",
    "Weekend Hours",
    "What is arjitha seva?",
    "What time does the temple open?",
    "When does the temple close?",
    "Where is the temple located?",
    "Who is the chairman?",
    "Who is the president?"
]
FALLBACK = "• I don’t have specific information on that right now."
# ---------------------------------------------------------
# Parametrized YES / NO test
# ---------------------------------------------------------
@pytest.mark.parametrize("query", USER_QUERIES)
def test_print_bot_response(query):
    response = answer_user(query)

    is_fallback = response.strip() == FALLBACK_RESPONSE

    print("\n" + "=" * 90)
    print(f"QUERY   : {query}")
    print(f"STATUS  : {'FALLBACK' if is_fallback else 'ANSWERED'}")
    print("RESPONSE:")
    print(response)
    print("=" * 90)

    logger.info(
        "QUERY='%s' | STATUS=%s",
        query,
        "FALLBACK" if is_fallback else "ANSWERED"
    )

    # Do NOT fail test for fallback — visibility only
    assert response is not None
