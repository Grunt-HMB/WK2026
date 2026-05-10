import re
import pandas as pd


GROUPS = list("ABCDEFGHIJKL")

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


def normalize_columns(df):
    if df is None:
        return None

    df = df.copy()
    df.columns = df.columns.astype(str).str.strip().str.lower()
    return df


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

    for nl, en in DUTCH_MONTHS.items():
        text = text.replace(nl, en)

    return text


def create_sort_columns(wedstrijden):
    wedstrijden = wedstrijden.copy()

    for col in ["datum", "tijd", "match_id", "match_id_sort"]:
        if col not in wedstrijden.columns:
            wedstrijden[col] = ""

    wedstrijden["datum_sort"] = pd.to_datetime(
        wedstrijden["datum"].apply(clean_dutch_date),
        format="%d %B %Y",
        errors="coerce",
    )

    wedstrijden["tijd_sort"] = pd.to_datetime(
        wedstrijden["tijd"].astype(str).str.strip(),
        format="%H:%M",
        errors="coerce",
    )

    wedstrijden["match_id_sort"] = pd.to_numeric(
        wedstrijden["match_id_sort"],
        errors="coerce",
    ).fillna(
        pd.to_numeric(wedstrijden["match_id"], errors="coerce")
    ).fillna(999999)

    return wedstrijden


def is_group_stage(stage):
    stage = str(stage or "").strip().lower()
    return stage.startswith("group ")


def is_knockout_stage(stage):
    return not is_group_stage(stage)


def get_group_letter(stage):
    stage = str(stage or "").strip().upper()
    match = re.search(r"GROUP\s+([A-L])", stage)

    if match:
        return match.group(1)

    return ""


def stage_title(stage):
    stage = str(stage or "").strip()

    titles = {
        "Round of 32": "🏆 1/16 finales",
        "Round of 16": "🏆 1/8 finales",
        "Quarterfinals": "🏆 Kwartfinales",
        "Semifinals": "🏆 Halve finales",
        "Third Place": "🥉 Troostwedstrijd",
        "Final": "🏆 Finale",
    }

    if stage in titles:
        return titles[stage]

    if is_group_stage(stage):
        return f"🌍 {stage}"

    return stage


def flag_img(code):
    code = str(code or "").strip().lower()

    if len(code) != 2:
        return ""

    return (
        f'<img src="https://flagcdn.com/w40/{code}.png" '
        f'style="width:30px;height:22px;object-fit:cover;border-radius:4px;'
        f'box-shadow:0 1px 3px rgba(0,0,0,0.25);vertical-align:middle;">'
    )
