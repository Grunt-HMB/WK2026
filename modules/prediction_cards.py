from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd


DUTCH_WEEKDAYS = [
    "maandag",
    "dinsdag",
    "woensdag",
    "donderdag",
    "vrijdag",
    "zaterdag",
    "zondag",
]

DUTCH_MONTHS = {
    "januari": "January",
    "februari": "February",
    "maart": "March",
    "april": "April",
    "mei": "May",
    "juni": "June",
    "juli": "July",
    "augustus": "August",
    "september": "September",
    "oktober": "October",
    "november": "November",
    "december": "December",
}


def get_value(row, *names):
    for name in names:
        if name in row and str(row.get(name, "")).strip() != "":
            return row.get(name, "")
    return ""


def clean_dutch_date(value):
    text = str(value or "").strip().lower()

    for day in DUTCH_WEEKDAYS:
        text = text.replace(day, "")

    text = " ".join(text.split())

    for nl_month, en_month in DUTCH_MONTHS.items():
        text = text.replace(nl_month, en_month)

    return text


def parse_match_datetime(match):
    datum = str(get_value(match, "datum", "date")).strip()
    tijd = str(get_value(match, "tijd", "uur", "time")).strip()

    if datum == "" or tijd == "":
        return None

    clean_date = clean_dutch_date(datum)
    datetime_text = f"{clean_date} {tijd}"

    parsed = pd.to_datetime(
        datetime_text,
        format="%d %B %Y %H:%M",
        errors="coerce",
    )

    if pd.isna(parsed):
        return None

    return parsed.to_pydatetime().replace(
        tzinfo=ZoneInfo("Europe/Brussels")
    )


def match_is_locked(match):
    match_datetime = parse_match_datetime(match)

    if match_datetime is None:
        return False

    now = datetime.now(ZoneInfo("Europe/Brussels"))

    return now >= match_datetime
