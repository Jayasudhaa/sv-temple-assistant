from datetime import datetime


def handle_arjitha_seva(q: str, now: datetime) -> str | None:
    if "arjitha" not in q:
        return None

    if any(w in q for w in ["what is", "meaning", "explain"]):
        return (
            "🪔 ARJITHA SEVA\n\n"
            "• Arjitha Seva is a special priest-performed service requested by individual devotees\n"
            "• Includes Abhishekam, Archana, Homam, Vrathams, and life-event ceremonies\n\n"
           
        )

    if any(w in q for w in ["list", "types", "available"]):
        return (
            "🪔 ARJITHA SEVAS AVAILABLE\n\n"
            "• Abhishekam\n"
            "• Archana\n"
            "• Homams\n"
            "• Vrathams\n"
            "• Life-event ceremonies (Samskaras)\n\n"
            
        )

    if any(w in q for w in ["how", "book", "schedule"]):
        return (
            "🪔 HOW TO BOOK ARJITHA SEVA\n\n"
            "• Decide the seva type\n"
            "• Choose temple or home\n"
            "• Contact temple to confirm date and priest availability\n\n"
            
        )
    return (
            "🪔 ARJITHA SEVA\n\n"
            "• Arjitha Seva is a special priest-performed service requested by individual devotees\n"
            "• Includes Abhishekam, Archana, Homam, Vrathams, and life-event ceremonies\n\n"
            "• Do you want to book any abhishekams, archana, homams or life -event ceremonies\n\n"
            
        )  
