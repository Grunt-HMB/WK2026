from datetime import datetime
from zoneinfo import ZoneInfo

from modules.settings import APP_TIMEZONE, TOURNAMENT_START


def now_brussels():
    return datetime.now(ZoneInfo(APP_TIMEZONE))


def timestamp():
    return now_brussels().strftime("%Y-%m-%d %H:%M:%S")


def tournament_locked():
    return now_brussels() >= TOURNAMENT_START


def safe_int(value):
    try:
        if value is None:
            return None

        if str(value).strip() == "":
            return None

        return int(float(value))

    except Exception:
        return None


def flag_emoji(country_code):
    """
    Zet ISO-2 landcode om naar vlag.
    BE -> 🇧🇪
    MX -> 🇲🇽
    ZA -> 🇿🇦
    """

    code = str(country_code or "").strip().upper()

    if len(code) != 2:
        return ""

    if not code.isalpha():
        return ""

    first = chr(ord(code[0]) + 127397)
    second = chr(ord(code[1]) + 127397)

    return first + second


def result_from_score(score1, score2):
    s1 = safe_int(score1)
    s2 = safe_int(score2)

    if s1 is None or s2 is None:
        return ""

    if s1 > s2:
        return "1"

    if s2 > s1:
        return "2"

    return "X"
