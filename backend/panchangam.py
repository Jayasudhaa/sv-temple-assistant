
#backend/panchangam.py
# 

import logging
import os
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
from datetime import datetime,timedelta,date
import re
from backend.get_timing import parse_explicit_date
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
MAASA_FILE = BASE_DIR/"data_raw"/"Panchang"/"2026"/"Maasa_Paksham.txt"


def infer_paksham_from_tithi(tithi_line: str) -> str | None:
    l = tithi_line.lower()

    if "purnima" in l:
        return "Shukla Paksha"
    if "amavasya" in l:
        return "Krishna Paksha"

    # fallback hints
    if "shukla" in l:
        return "Shukla Paksha"
    if "krishna" in l:
        return "Krishna Paksha"

    return None

def get_today_panchang(now: datetime) -> list[str]:
    year = now.year
    month_full = now.strftime("%B").lower()
    month_abbr = now.strftime("%b").lower()
    day = now.day

    base = os.path.join("data_raw", "Panchang", str(year))
    file_path = os.path.join(base, f"{month_full}_{year}_panchang.txt")

    if not os.path.exists(file_path):
        logger.error("Panchang file not found: %s", file_path)
        return []

    with open(file_path, "r", encoding="utf-8") as f:
        rows = f.readlines()

    results = []
    capture = False

    date_re = re.compile(
        rf"\b({month_abbr}|{month_full})\s+0*{day}(st|nd|rd|th)?\b",
        re.IGNORECASE
    )

    next_date_re = re.compile(
        rf"\b({month_abbr}|{month_full})\s+\d{{1,2}}",
        re.IGNORECASE
    )

    paksham = None

    for row in rows:
        clean = row.strip()

        if date_re.search(clean):
            capture = True
            results.append(clean)
            continue

        if capture:
            if next_date_re.search(clean):
                break

            # TITHI LINE
            if "tithi" in clean.lower():
                results.append(clean)

                inferred = infer_paksham_from_tithi(clean)
                if inferred:
                    paksham = inferred

            # OTHER LINES
            elif any(k in clean.lower() for k in [
                "nakshatra", "event:"
            ]):
                results.append(clean)

    if paksham:
        results.insert(1, f"Paksham: {paksham}")

    return results


def handle_panchang(q: str, now: datetime) -> str | None:
    if not any(w in q for w in ["panchang", "tithi", "nakshatra", "star", "maasa", "paksham"]):
        return None

    explicit_date = parse_explicit_date(q, now)

    if explicit_date:
        target_date = explicit_date
        label = target_date.strftime("%B %d, %Y")
    elif any(w in q for w in ["tomorrow", "tomo"]):
        target_date = now + timedelta(days=1)
        label = "Tomorrow"
    else:
        target_date = now
        label = "Today"

    lines = get_today_panchang(target_date)

    maasa_info = get_maasa_paksham(target_date.date())
    logger.info("maasa paksham %s", maasa_info)
    maasa_line = ""
    if maasa_info:
        maasa, paksham = maasa_info
        maasa_line = f"🪔 Maasa: {maasa}\n🌗 Paksham: {paksham}\n"

    if not lines:
        return f"🌙 {label}'s Panchang is not listed."

    # Intent filters
    if "tithi" in q:
        filtered = [l for l in lines if "tithi" in l.lower()]
        if filtered:
            return (
                f"🌙 {label}'s Tithi\n"
                f"{maasa_line}"
                + "\n".join(f"• {l}" for l in filtered)
            )

    if "nakshatra" in q or "star" in q:
        filtered = [l for l in lines if "nakshatra" in l.lower()]
        if filtered:
            return (
                f"🌙 {label}'s Nakshatra\n"
                f"{maasa_line}"
                + "\n".join(f"• {l}" for l in filtered)
            )

    # Full Panchang
    out = [
        f"🌙 {label}'s Panchang ({target_date:%B %d, %Y})",
        maasa_line.rstrip(),
    ]
    out.extend(f"• {l}" for l in lines)
    return "\n".join(out)


def get_maasa_paksham(target_date: date) -> tuple[str, str] | None:
    logger.info("Resolved MAASA_FILE = %s", MAASA_FILE.resolve())
    logger.info("Files in Panchang/2026: %s",
            list((BASE_DIR / "data_raw" / "Panchang" / "2026").iterdir()))

    if not MAASA_FILE.exists():
        logger.error("❌ Maasa_Paksham.txt NOT FOUND")
        return None

    month = target_date.strftime("%b")   # Jan, Feb, ...
    day = target_date.day

    current_maasa: str | None = None

    with MAASA_FILE.open(encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()

            # ─────────────────────────────────────────
            # 1️⃣ Detect MAASA header
            # Example: MONTH 1: PUSHYA MAASA (January 1-18)
            # ─────────────────────────────────────────
            m = re.match(r"MONTH\s+\d+:\s+([A-Z\s]+)\s+MAASA", line)
            if m:
                current_maasa = f"{m.group(1).title()} Maasa"
                logger.info("Detected Maasa header: %s", current_maasa)
                continue

            # Skip until a Maasa is known and row contains '|'
            if not current_maasa or "|" not in line:
                continue

            # ─────────────────────────────────────────
            # 2️⃣ Parse date range + paksham
            # Example rows:
            # Jan 1-18 | Sukla Paksham | ...
            # Jan 19-Feb 1 | Krishna Paksham | ...
            # ─────────────────────────────────────────
            parts = [p.strip() for p in line.split("|")]
            if len(parts) < 2:
                continue

            date_range, paksham = parts[0], parts[1]

            if "-" not in date_range or "Paksham" not in paksham:
                continue

            try:
                start, end = date_range.split("-")

                # Start date
                sm, sd = start.split()
                sd = int(sd)

                # End date (handle both formats)
                end_parts = end.split()
                if len(end_parts) == 1:
                    # Jan 1-18
                    em = sm
                    ed = int(end_parts[0])
                else:
                    # Jan 19-Feb 1
                    em, ed = end_parts
                    ed = int(ed)

            except Exception as e:
                logger.warning("Skipping malformed line: %s | error=%s", line, e)
                continue

            # ─────────────────────────────────────────
            # 3️⃣ Match date
            # ─────────────────────────────────────────
            if sm == em:
                if sm == month and sd <= day <= ed:
                    return current_maasa, paksham
            else:
                if (month == sm and day >= sd) or (month == em and day <= ed):
                    return current_maasa, paksham

    logger.warning("⚠️ No Maasa/Paksham match for %s", target_date)
    return None