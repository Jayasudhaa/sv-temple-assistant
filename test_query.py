from backend.ask_temple import answer_user

from datetime import datetime,date,time
from zoneinfo import ZoneInfo


message_ts = int(datetime.now(ZoneInfo("America/Denver")).timestamp())

def test_vishnu_sahasranam_no_context_leakage():
    
    out = answer_user(" sudarshana homam cost", message_ts=message_ts)
 
    print("\n===== BOT RESPONSE =====\n")
    print(out)

    lowered = out.lower()

    forbidden = [
        "provided temple context",
        "does not contain",
        "not mentioned",
        "documents",
        "context does not",
    ]

    for phrase in forbidden:
        assert phrase not in lowered


