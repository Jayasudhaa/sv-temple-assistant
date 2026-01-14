from datetime import datetime
import os


STORY_INTENT_MAP = [
    ("varalakshmi vratham", "Rituals/Varalakshmi_Vratham.txt"),
    ("varalakshmi", "Rituals/Varalakshmi_Vratham.txt"),
    ("guru poornima", "Rituals/Guru_Poornima.txt"),
    ("guru purnima", "Rituals/Guru_Poornima.txt"),
    ("mahalakshmi jayanthi", "Rituals/Mahalakshmi_Jayanthi.txt"),
    ("mahalakshmi jayanti", "Rituals/Mahalakshmi_Jayanthi.txt"),
    ("diwali", "Rituals/story_of_Diwali.txt"),
    ("deepavali", "Rituals/story_of_Diwali.txt"),
]

def handle_story_query(q: str) -> str | None:
    """Handle story queries by loading from Rituals directory"""
    q = q
    
    for key, filename in STORY_INTENT_MAP:
        if key in q and any(w in q for w in ["story", "significance", "meaning", "why", "about"]) \
            and not any(w in q for w in ["date", "dates", "when"]):
            # Correct path with Rituals already in filename
            path = os.path.join("data_raw", filename)
            
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                        if content:
                            return (content)
                except Exception as e:
                    print(f"Error reading {path}: {e}")
            else:
                print(f"Story file not found: {path}")
    
    return None

def handle_story(q: str, now: datetime) -> str | None:
    return handle_story_query(q)
