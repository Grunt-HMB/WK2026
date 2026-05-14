import streamlit as st
import pandas as pd

from modules.database import (
    load_matches,
    load_predictions,
    batch_save_predictions,
)

st.set_page_config(
    page_title="WK 2026",
    page_icon="⚽",
    layout="centered",
    initial_sidebar_state="collapsed",
)

USER_ID = "Tom"


# =========================================================
# HELPERS
# =========================================================

def country_flag(code):
    code = str(code or "").strip().upper()

    if len(code) != 2:
        return "⚽"

    return chr(ord(code[0]) + 127397) + chr(ord(code[1]) + 127397)


def format_date(value):
    txt = str(value or "").strip()

    # 11-06-26 -> 11/06
    parts = txt.split("-")
    if len(parts) >= 2:
        return f"{parts[0]}/{parts[1]}"

    return txt


def format_time(value):
    txt = str(value or "").strip()

    # 21:00:00 -> 21:00
    if txt.count(":") >= 2:
        return ":".join(txt.split(":")[:2])

    return txt


def get_prediction(match_id):
    data = st.session_state.local_predictions.get(str(match_id), "X")

    if isinstance(data, dict):
        value = data.get("prediction", "X")
    else:
        value = data

    value = str(value).upper().strip()

    if value not in ["1", "X", "2"]:
        return "X"

    return value


def save_all_predictions():
    to_save = {}

    for key, value in st.session_state.items():
        if not key.startswith("pred_"):
            continue

        match_id = key.replace("pred_", "")
        prediction = str(value).upper().strip()

        if prediction not in ["1", "X", "2"]:
            prediction = "X"

        to_save[match_id] = {
            "prediction": prediction,
            "score1": "",
            "score2": "",
        }

    if not to_save:
        return 0

    count = batch_save_predictions(
        USER_ID,
        to_save,
        "concept",
    )

    st.cache_data.clear()
    return count


# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>

.block-container {
    max-width: 800px;
    padding-top: 0 !important;
    padding-left: 0.45rem !important;
    padding-right: 0.45rem !important;
    padding-bottom: 5rem !important;
}

section[data-testid="stSidebar"] {
    display: none;
}

/* =========================================================
TOP BAR
========================================================= */

.st-key-top_bar {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    right: 0 !important;
    z-index: 999999 !important;

    background: #0e1117 !important;
    padding: 0.45rem 0.55rem 0.5rem 0.55rem !important;
    border-bottom: 1px solid rgba(255,255,255,0.12);
}

.st-key-top_bar > div {
    max-width: 800px;
    margin-left: auto;
    margin-right: auto;
}

.top-spacer {
    height: 175px;
}

.st-key-top_bar div[data-testid="stAlert"] {
    padding: 0.38rem 0.6rem !important;
    font-size: 0.76rem !important;
    margin-bottom: 0.25rem !important;
    border-radius: 10px !important;
}

.st-key-top_bar button {
    min-height: 36px !important;
    height: 36px !important;
    border-radius: 10px !important;
    font-weight: 800 !important;
}

/* =========================================================
MENU BUTTONS
========================================================= */

.menu-row button {
    font-size: 0.78rem !important;
    padding: 0.2rem 0.1rem !important;
}

/* =========================================================
MATCH CARD
========================================================= */

[class*="st-key-match_card_"] {
    background: #111827;
    border: 1px solid rgba(255,255,255,0.13);
    border-radius: 13px;
    padding: 0.6rem !important;
    margin-bottom: 0.5rem;
}

.match-info {
    display: grid;
    grid-template-columns: 62px 1fr;
    gap: 0.55rem;
    align-items: center;
}

.match-date {
    font-size: 0.78rem;
    color: #cbd5e1;
    text-align: center;
    line-height: 1.15;
}

.match-date .ball {
    color: #22c55e;
    font-size: 0.9rem;
    font-weight: 900;
}

.match-teams {
    font-size: 0.9rem;
    font-weight: 800;
    line-height: 1.28;
    min-width: 0;
}

.team-line {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* 1/X/2 */
[class*="st-key-match_card_"] div[data-testid="stSegmentedControl"] {
    margin-top: 0.45rem !important;
}

[class*="st-key-match_card_"] div[data-testid="stSegmentedControl"] button {
    min-width: