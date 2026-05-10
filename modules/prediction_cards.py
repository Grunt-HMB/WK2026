from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import streamlit as st

from modules.prediction_state import set_prediction


LOCAL_TZ = ZoneInfo("Europe/Brussels")

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
    "januari": "01",
    "februari": "02",
    "maart": "03",
    "april": "04",
    "mei": "05",
    "juni": "06",
    "juli": "07",
    "augustus": "08",
    "september": "09",
    "oktober": "10",
    "november": "11",
    "december": "12",
}


def flag_img(code):
    code = str(code or "").strip().lower()

    if len(code) != 2:
        return ""

    return (
        f'<img src="https://flagcdn.com/w40/{code}.png" '
        f'style="width:30px;height:22px;object-fit:cover;border-radius:4px;'
        f'box-shadow:0 1px 3px rgba(0,0,0,0.25);vertical-align:middle;">'
    )


def clean_dutch_date(date_value):
    text = str(date_value or "").strip().lower()

    if not text:
        return ""

    for weekday in DUTCH_WEEKDAYS:
        text = text.replace(weekday, "")

    text = " ".join(text.split())

    for month_name, month_number in DUTCH_MONTHS.items():
        text = text.replace(month_name, month_number)

    return text.strip()


def parse_match_datetime(date_value, time_value):
    date_text = clean_dutch_date(date_value)
    time_text = str(time_value or "").strip()

    if not date_text or not time_text:
        return None

    raw = f"{date_text} {time_text}"

    formats = [
        "%d %m %Y %H:%M",
        "%d %m %y %H:%M",
        "%d-%m-%Y %H:%M",
        "%d-%m-%y %H:%M",
        "%d/%m/%Y %H:%M",
        "%d/%m/%y %H:%M",
        "%d %m %Y %H:%M:%S",
        "%d %m %y %H:%M:%S",
        "%d-%m-%Y %H:%M:%S",
        "%d-%m-%y %H:%M:%S",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%y %H:%M:%S",
    ]

    for fmt in formats:
        try:
            naive_dt = datetime.strptime(raw, fmt)
            return naive_dt.replace(tzinfo=LOCAL_TZ)
        except Exception:
            pass

    return None


def match_is_locked(match):
    match_dt = parse_match_datetime(
        match.get("datum", ""),
        match.get("tijd", ""),
    )

    if match_dt is None:
        return False

    lock_dt = match_dt - timedelta(hours=1)
    now_local = datetime.now(LOCAL_TZ)

    return now_local >= lock_dt


def prediction_label(choice, selected):
    choice = str(choice)
    selected = str(selected or "").upper()

    if selected == choice:
        return f"✅ {choice}"

    return choice


def render_prediction_buttons(match, match_id, selected, disabled):
    locked = match_is_locked(match)
    button_disabled = disabled or locked

    c1, cx, c2 = st.columns(3, gap="small")

    with c1:
        if st.button(
            prediction_label("1", selected),
            key=f"btn_1_{match_id}",
            use_container_width=True,
            disabled=button_disabled,
        ):
            if match_is_locked(match):
                st.warning("Deze wedstrijd is gesloten.")
                st.rerun()

            set_prediction(match_id, "1")
            st.rerun()

    with cx:
        if st.button(
            prediction_label("X", selected),
            key=f"btn_x_{match_id}",
            use_container_width=True,
            disabled=button_disabled,
        ):
            if match_is_locked(match):
                st.warning("Deze wedstrijd is gesloten.")
                st.rerun()

            set_prediction(match_id, "X")
            st.rerun()

    with c2:
        if st.button(
            prediction_label("2", selected),
            key=f"btn_2_{match_id}",
            use_container_width=True,
            disabled=button_disabled,
        ):
            if match_is_locked(match):
                st.warning("Deze wedstrijd is gesloten.")
                st.rerun()

            set_prediction(match_id, "2")
            st.rerun()


def render_match_card(match, disabled):
    match_id = str(match["match_id"]).strip()

    team1 = str(match.get("team1", ""))
    team2 = str(match.get("team2", ""))

    code1 = str(match.get("team1_code", "")).upper()
    code2 = str(match.get("team2_code", "")).upper()

    flag1 = flag_img(code1)
    flag2 = flag_img(code2)

    date = str(match.get("datum", ""))
    time = str(match.get("tijd", ""))

    current = st.session_state["local_predictions"].get(match_id, {})
    selected = str(current.get("prediction", "")).upper()

    score1 = current.get("score1", "")
    score2 = current.get("score2", "")

    middle = f"{score1}-{score2}" if score1 != "" and score2 != "" else "-"

    locked = match_is_locked(match)

    lock_text = ""
    if locked:
        lock_text = (
            '<span style="color:#ef4444;font-weight:900;margin-left:8px;">'
            "🔒 gesloten"
            "</span>"
        )

    with st.container(border=True):
        col_info, col_buttons = st.columns([7.2, 2.0], gap="small")

        with col_info:
            html = (
                '<div class="match-row">'
                f'<div class="match-date">{date}<br>{time}{lock_text}</div>'
                '<div class="match-teams">'
                '<div class="team-left">'
                f'<span>{flag1}</span>'
                f'<span class="team-name">{team1}</span>'
                "</div>"
                f'<div class="match-score">{middle}</div>'
                '<div class="team-right">'
                f'<span>{flag2}</span>'
                f'<span class="team-name">{team2}</span>'
                "</div>"
                "</div>"
                "</div>"
            )

            st.markdown(html, unsafe_allow_html=True)

        with col_buttons:
            render_prediction_buttons(match, match_id, selected, disabled)
