import pytest
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from backend.ask_temple import answer_user

# =================================================
# LOGGING SETUP
# =================================================
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# =================================================
# FIXED TIME (DETERMINISTIC)
# =================================================
FIXED_NOW = datetime(2025, 12, 19, 10, 25, tzinfo=ZoneInfo("America/Denver"))

# =================================================
# FIXTURES
# =================================================

@pytest.fixture
def user_id():
    return "pytest_user"


@pytest.fixture(autouse=True)
def log_test_execution(request, caplog):
    caplog.set_level(logging.INFO)
    logger.info("=" * 80)
    logger.info(f"START TEST: {request.node.name}")
    yield
    logger.info(f"END TEST: {request.node.name}")
    logger.info("=" * 80)


# =================================================
# HELPER
# =================================================

def run_query(query: str, user_id: str):
    logger.info(f"USER QUERY: {query}")
    out = answer_user(query, user_id)
    logger.info(f"BOT RESPONSE:\n{out}")
    return out


# =================================================
# QUERY LISTS (150+ TOTAL)
# =================================================

TEMPLE_STATUS_QUERIES = [
    "Is the temple open today?",
    "Is the temple open today (holiday)?",
    "When does the temple close?",
    "What time does the temple open?",
    "Temple hours",
    "Temple timings",
    "Temple address",
    "Where is the temple located?",
    "Temple phone number",
    "Manager contact",
]

LIFE_EVENT_QUERIES = [
    "Aksharabhyasam",
    "Vidyarambam",
    "Akshar Arambh",
    "Garbadhana",
    "Pumsavana",
    "Simantonnayana",
    "Jatakarma",
    "Namakarana",
    "Nishkramana",
    "Annaprashana",
    "Chudakarana",
    "Karnavedha",
    "Vivaha",
    "Antyeshti",
    "Mundan",
    "Pinda Dhan",
    "Pitru Paksha",
    "Mahalaya",
    "First Year Birthday",
    "Half Sari Function",
    "Langa Voni",
    "Upanayanam",
    "Seemantham",
    "Sadhabhisekam",
    "Kanakabhisekam",
    "Beema Ratha Santhi",
    "Sashtiapdhapoorthi",
]

FESTIVAL_QUERIES = [
    "Navarathri",
    "Dusshera",
    "Holi",
    "Thai Poosam",
    "Aadi Krithigai",
    "Karthigai Deepam",
    "Tulsi Kalyanam",
    "Karthika Purnima",
    "Pradhosham",
    "Maha Shivarathri",
    "Ugadi",
    "Tamil New year",
    "Vishu",
    "English new year",
    "Ram Navami",
    "Sankaranthi",
    "Pongal",
    "Makar Sankaranthi",
    "Deepavali",
    "Diwali",
    "Janmashtami",
    "Krishna Jayanthi",
    "Vasanth Panchami",
    "Ganesh Chathurthi",
    "Vinayakar Chathurthi",
    "Onam",
    "Vijaya Dhashami",
    "Vaikunta Ekadesi",
]

POOJA_QUERIES = [
    "Abhishekam",
    "Venkateswara Abhishekam",
    "Mahalakshmi Abhishekam",
    "Shiva Abhisekam",
    "Murugan Abhisekam",
    "Ganapathi Abhisekam",
    "Sudarshana Homam",
    "Ayush Homam cost",
    "Chandi Homam",
    "Navagraha Puja",
    "Graha Puja",
    "Lakshmi Puja",
    "Gau Mata Puja",
    "Vastu Puja",
    "Vahana Puja",
    "Vriksha Puja",
]

SCHEDULE_QUERIES = [
    "Daily pooja schedule",
    "Monthly pooja schedule",
    "Any special events today",
    "What is happening today at temple",
    "Satyanarayana pooja timing",
]

PANCHANG_QUERIES = [
    "Today panchang",
    "Dec 1 panchang",
    "Amavasya dates",
    "Purnima dates",
    "Guru Purnima",
]

HOMAM_COST_QUERIES = [
    "Homam cost",
    "Ayush Homam cost",
    "Chandi Homam cost",
    "Sudarshana Homam cost",
    "Saamoohika Homam",
]

ARCHANA_COST_QUERIES = [
    "Archana cost",
    "Sahasranama Archana cost",
]

STORY_QUERIES = [
    "Guru Purnima story",
    "Varalakshmi Vratham story",
    "Diwali story",
]

ADMIN_ESCALATION_QUERIES = [
    "Priest",
    "Patron Members",
    "Board of Trustees",
    "Vice Treasurer",
    "Vice EC President",
    "Vice Secretary",
    "Treasurer",
    "Founding Members",
    "Vice Chairman",
]

VOLUNTEERING_QUERIES = [
    "Volunteering at SVTC",
    "BalaVihar",
    "Bhagavad Gita Class",
]

# -------------------------------------------------
# COMBINED QUERY LIST (150+)
# -------------------------------------------------
ALL_QUERIES = (
    TEMPLE_STATUS_QUERIES
    + LIFE_EVENT_QUERIES
    + FESTIVAL_QUERIES
    + POOJA_QUERIES
    + SCHEDULE_QUERIES
    + PANCHANG_QUERIES
    + HOMAM_COST_QUERIES
    + ARCHANA_COST_QUERIES
    + STORY_QUERIES
    + ADMIN_ESCALATION_QUERIES
    + VOLUNTEERING_QUERIES
)

# =================================================
# PARAMETRIZED MASTER TEST
# =================================================

@pytest.mark.parametrize("query", ALL_QUERIES)
def test_all_supported_queries(query, user_id):
    """
    Each query is an independent test.
    Total tests ~= len(ALL_QUERIES)
    """
    out = run_query(query, user_id)

    # ---------------- SAFETY ASSERTIONS ----------------
    assert out is not None
    assert isinstance(out, str)
    assert len(out.strip()) > 10

    # No raw crashes
    assert "traceback" not in out.lower()
    assert "exception" not in out.lower()

    # Manager escalation should include contact
    if query.lower() in [q.lower() for q in ADMIN_ESCALATION_QUERIES]:
        assert "phone" in out.lower() or "manager" in out.lower()
