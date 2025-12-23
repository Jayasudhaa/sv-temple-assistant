import pytest
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from backend.ask_temple import answer_user

# -------------------------------------------------
# LOGGING SETUP
# -------------------------------------------------
logger = logging.getLogger(__name__)

# -------------------------------------------------
# FIXED TIME FOR DETERMINISTIC TESTS
# -------------------------------------------------
FIXED_NOW = datetime(2025, 12, 19, 10, 25, tzinfo=ZoneInfo("America/Denver"))

# -------------------------------------------------
# GLOBAL FIXTURES
# -------------------------------------------------

@pytest.fixture
def user_id():
    return "pytest_user"


@pytest.fixture(autouse=True)
def log_test_execution(request, caplog):
    caplog.set_level(logging.INFO)

    logging.info("=" * 70)
    logging.info(f"START TEST: {request.node.name}")

    yield

    logging.info(f"END TEST: {request.node.name}")
    logging.info("=" * 70)



# -------------------------------------------------
# HELPER TO LOG QUERY + RESPONSE
# -------------------------------------------------

def run_query(query: str, user_id: str):
    logging.info(f"USER QUERY: {query}")
    out = answer_user(query, user_id)
    logging.info(f"BOT RESPONSE:\n{out}")
    return out



# =================================================
# STORY TESTS
# =================================================

def test_varalakshmi_story(user_id):
    out = run_query("tell me varalakshmi vratham story", user_id)
    assert "Varalakshmi" in out or "Vratham" in out


def test_guru_poornima_story(user_id):
    out = run_query("guru poornima story", user_id)
    assert "Guru" in out or "Poornima" in out


def test_diwali_story(user_id):
    out = run_query("diwali story", user_id)
    assert "Diwali" in out or "Deepavali" in out


# =================================================
# PANCHANG TESTS
# =================================================

def test_today_panchang(user_id):
    out = run_query("today panchang", user_id)
    assert "Panchang" in out or "Tithi" in out


def test_specific_date_panchang(user_id):
    out = run_query("dec 1 panchang", user_id)
    assert "Dec" in out or "Panchang" in out


# =================================================
# DAILY POOJA TESTS
# =================================================

def test_daily_pooja(user_id):
    out = run_query("daily pooja schedule", user_id)
    assert "Suprabhata" in out
    assert "Archana" in out


# =================================================
# ABHISHEKAM TESTS
# =================================================

def test_mahalakshmi_abhishekam(user_id):
    out = run_query("when is mahalakshmi abhishekam", user_id)
    assert "Saturday" in out
    assert "Mahalakshmi" in out


def test_venkateswara_abhishekam(user_id):
    out = run_query("venkateswara abhishekam schedule", user_id)
    assert "Abhishekam" in out or "Saturday" in out


# =================================================
# TEMPLE HOURS TESTS
# =================================================

def test_when_does_temple_close(user_id):
    out = run_query("when does temple close", user_id)
    assert "close" in out.lower()


def test_is_temple_open_today(user_id):
    out = run_query("is temple open today", user_id)
    assert "open" in out.lower() or "closed" in out.lower()


# =================================================
# ARJITHA SEVA TESTS
# =================================================

def test_arjitha_seva_explain(user_id):
    out = run_query("what is arjitha seva", user_id)
    assert "Arjitha Seva" in out


def test_arjitha_seva_list(user_id):
    out = run_query("list arjitha sevas", user_id)
    assert "Abhishekam" in out
    assert "Homam" in out


def test_arjitha_seva_booking(user_id):
    out = run_query("how to book arjitha seva", user_id)
    assert "contact" in out.lower()


# =================================================
# REGRESSION / GUARD TESTS
# =================================================

def test_story_does_not_trigger_rag(user_id):
    out = run_query("varalakshmi story", user_id)
    assert "contact the temple" not in out.lower()


def test_no_empty_response(user_id):
    out = run_query("random unknown query", user_id)
    assert len(out.strip()) > 10

# =====================================================
# ARJITHA SEVA
# =====================================================

def test_arjitha_seva_explanation(user_id):
    logger.info("Testing Arjitha Seva explanation")
    out = answer_user("what is arjitha seva", user_id)
    logger.info(out)
    assert "Arjitha Seva" in out
    assert "special" in out.lower()


def test_arjitha_seva_list(user_id):
    logger.info("Testing Arjitha Seva list")
    out = answer_user("list arjitha sevas", user_id)
    logger.info(out)
    assert "Abhishekam" in out
    assert "Homam" in out
    assert "Samskara" in out or "ceremony" in out.lower()


def test_arjitha_seva_booking(user_id):
    logger.info("Testing Arjitha Seva booking flow")
    out = answer_user("how to book arjitha seva", user_id)
    logger.info(out)
    assert "contact" in out.lower()
    assert "phone" in out.lower()


# =====================================================
# ABHISHEKAM
# =====================================================

def test_mahalakshmi_abhishekam(user_id):
    logger.info("Testing Mahalakshmi Abhishekam")
    out = answer_user("when is mahalakshmi abhishekam", user_id)
    logger.info(out)
    assert "Saturday" in out
    assert "Abhishekam" in out


def test_sudarshana_abhishekam(user_id):
    logger.info("Testing Sudarshana Homam")
    out = answer_user("when is sudarshana homam", user_id)
    logger.info(out)
    assert "Sunday" in out or "Homam" in out


def test_abhishekam_cost(user_id):
    logger.info("Testing Abhishekam sponsorship")
    out = answer_user("abhishekam cost", user_id)
    logger.info(out)
    assert "$" in out
    assert "sponsorship" in out.lower()


# =====================================================
# DAILY / MONTHLY POOJA
# =====================================================

def test_daily_pooja_schedule(user_id):
    logger.info("Testing daily pooja schedule")
    out = answer_user("daily pooja schedule", user_id)
    logger.info(out)
    assert "Suprabhata" in out
    assert "Archana" in out


def test_monthly_pooja_schedule(user_id):
    logger.info("Testing monthly pooja schedule")
    out = answer_user("monthly pooja schedule", user_id)
    logger.info(out)
    assert "Full Moon" in out or "Satyanarayana" in out


# =====================================================
# PANCHANG / AMAVASYA
# =====================================================

def test_today_panchang(user_id):
    logger.info("Testing today's panchang")
    out = answer_user("today panchang", user_id)
    logger.info(out)
    assert "Panchang" in out or "Tithi" in out


def test_amavasya_dates(user_id):
    logger.info("Testing Amavasya dates")
    out = answer_user("amavasya dates", user_id)
    logger.info(out)
    assert "Amavasya" in out or "new moon" in out.lower()


# =====================================================
# LIFE EVENT CEREMONIES
# =====================================================

def test_aksharabhyasam_items(user_id):
    logger.info("Testing Aksharabhyasam items")
    out = answer_user("items for aksharabhyasam", user_id)
    logger.info(out)
    assert "aksharabhyasam" in out.lower()
    assert "Rice" in out or "Slate" in out


def test_gruhapravesam_items(user_id):
    logger.info("Testing Gruhapravesam items")
    out = answer_user("items for gruhapravesam", user_id)
    logger.info(out)
    assert "gruhapravesam" in out.lower()
    assert "Milk" in out or "Navadhanyam" in out


def test_satyanarayana_home(user_id):
    logger.info("Testing Satyanarayana pooja at home")
    out = answer_user("items for satyanarayana pooja at home", user_id)
    logger.info(out)
    assert "Satyanarayana" in out
    assert "home" in out.lower()


def test_satyanarayana_temple(user_id):
    logger.info("Testing Satyanarayana pooja at temple")
    out = answer_user("items for satyanarayana pooja", user_id)
    logger.info(out)
    assert "satyanarayana" in out.lower()
    assert "Full Moon" in out or "6:30" in out


# =====================================================
# VASTRAM
# =====================================================

def test_vastram_samarpanam(user_id):
    logger.info("Testing Vastram Samarpanam")
    out = answer_user("vastram samarpanam cost", user_id)
    logger.info(out)
    assert "$" in out
    assert "Vastram" in out


# =====================================================
# TEMPLE HOURS
# =====================================================

def test_temple_closing_time(user_id):
    logger.info("Testing temple closing time")
    out = answer_user("when does temple close", user_id)
    logger.info(out)
    assert "close" in out.lower()


def test_temple_open_today(user_id):
    logger.info("Testing temple open today")
    out = answer_user("is temple open today", user_id)
    logger.info(out)
    assert "open" in out.lower() or "closed" in out.lower()


# =====================================================
# STORY GUARD TESTS
# =====================================================

def test_varalakshmi_story(user_id):
    logger.info("Testing Varalakshmi story")
    out = answer_user("varalakshmi vratham story", user_id)
    logger.info(out)
    assert "Varalakshmi" in out


def test_guru_poornima_story(user_id):
    logger.info("Testing Guru Poornima story")
    out = answer_user("guru poornima story", user_id)
    logger.info(out)
    assert "Guru" in out


def test_diwali_story(user_id):
    logger.info("Testing Diwali story")
    out = answer_user("diwali story", user_id)
    logger.info(out)
    assert "Diwali" in out or "Deepavali" in out


# =====================================================
# REGRESSION / SAFETY
# =====================================================

def test_no_empty_response(user_id):
    logger.info("Testing fallback response")
    out = answer_user("some unknown question", user_id)
    logger.info(out)
    assert len(out.strip()) > 20