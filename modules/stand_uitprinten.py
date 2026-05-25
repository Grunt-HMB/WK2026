import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

MATCHES_SHEET = "Matches"
PREDICTIONS_SHEET = "Predictions"

PREDICTION_HEADERS = [
    "user_id",
    "match_id",
    "prediction",
    "score1",
    "score2",
    "status",
    "timestamp",
]


@st.cache_resource
def connect_results_sheet():
    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES,
    )
    client = gspread.authorize(credentials)
    return client.open_by_key(st.secrets["GOOGLE_RESULTS_SHEET_ID"])


@st.cache_data(ttl=60)
def load_results_matches():
    sh = connect_results_sheet()
    ws = sh.worksheet(MATCHES_SHEET)

    values = ws.get_all_values()
    empty_df = pd.DataFrame(columns=["match_id", "datum_tijd", "team1", "team2"])

    if not values:
        return empty_df

    header_row_index = None

    for i, row in enumerate(values):
        clean_row = [str(c).strip() for c in row]
        if "Match No." in clean_row and "Team 1" in clean_row and "Team 2" in clean_row:
            header_row_index = i
            break

    if header_row_index is None:
        st.error("Kon de headerregel in tabblad 'Matches' niet vinden.")
        return empty_df

    headers = [str(c).strip() for c in values[header_row_index]]
    data_rows = values[header_row_index + 1:]

    fixed_rows = []
    for row in data_rows:
        row = row[:len(headers)] + [""] * max(0, len(headers) - len(row))
        fixed_rows.append(row)

    raw_df = pd.DataFrame(fixed_rows, columns=headers)

    date_col = ""
    for possible in ["Date (my time)", "Date  (my time)", "datum_tijd", "datum"]:
        if possible in raw_df.columns:
            date_col = possible
            break

    df = pd.DataFrame()
    df["match_id"] = raw_df["Match No."].astype(str).str.strip()
    df["team1"] = raw_df["Team 1"].astype(str).str.strip()
    df["team2"] = raw_df["Team 2"].astype(str).str.strip()
    df["datum_tijd"] = raw_df[date_col].astype(str).str.strip() if date_col else ""

    df = df[
        (df["match_id"] != "")
        & (df["team1"] != "")
        & (df["team2"] != "")
    ].copy()

    return df[["match_id", "datum_tijd", "team1", "team2"]]


@st.cache_data(ttl=30)
def load_results_predictions():
    sh = connect_results_sheet()
    ws = sh.worksheet(PREDICTIONS_SHEET)

    values = ws.get_all_values()

    if not values:
        return pd.DataFrame(columns=PREDICTION_HEADERS)

    headers = [str(c).strip() for c in values[0]]
    data_rows = values[1:]

    fixed_rows = []
    for row in data_rows:
        row = row[:len(headers)] + [""] * max(0, len(headers) - len(row))
        fixed_rows.append(row)

    raw_df = pd.DataFrame(fixed_rows, columns=headers)

    for col in PREDICTION_HEADERS:
        if col not in raw_df.columns:
            raw_df[col] = ""

    df = raw_df[PREDICTION_HEADERS].copy()

    for col in PREDICTION_HEADERS:
        df[col] = df[col].astype(str).str.strip()

    df = df[(df["user_id"] != "") & (df["match_id"] != "")].copy()

    return df


def save_predictions_to_sheet(user_id, local_predictions):
    sh = connect_results_sheet()
    ws = sh.worksheet(PREDICTIONS_SHEET)

    existing_df = load_results_predictions()

    if existing_df.empty:
        existing_df = pd.DataFrame(columns=PREDICTION_HEADERS)

    rows_to_keep = existing_df[
        existing_df["user_id"].astype(str).str.strip() != str(user_id)
    ].copy()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    new_rows = []

    for match_id, pred in local_predictions.items():
        prediction = str(pred.get("prediction", "")).strip()
        score1 = str(pred.get("score1", "")).strip()
        score2 = str(pred.get("score2", "")).strip()

        if prediction == "" and score1 == "" and score2 == "":
            continue

        new_rows.append({
            "user_id": str(user_id),
            "match_id": str(match_id),
            "prediction": prediction,
            "score1": score1,
            "score2": score2,
            "status": "concept",
            "timestamp": now,
        })

    new_df = pd.DataFrame(new_rows, columns=PREDICTION_HEADERS)

    final_df = pd.concat(
        [rows_to_keep[PREDICTION_HEADERS], new_df],
        ignore_index=True,
    )

    output = [PREDICTION_HEADERS] + final_df.fillna("").values.tolist()

    ws.batch_clear(["A:G"])
    ws.update("A1", output)

    st.cache_data.clear()


def init_local_predictions(user_id):
    if "stand_local_user" not in st.session_state:
        st.session_state.stand_local_user = None

    if "stand_local_predictions" not in st.session_state:
        st.session_state.stand_local_predictions = {}

    if st.session_state.stand_local_user == user_id:
        return

    predictions_df = load_results_predictions()

    user_df = predictions_df[
        predictions_df["user_id"] == str(user_id)
    ].copy()

    local = {}

    for _, row in user_df.iterrows():
        match_id = str(row.get("match_id", "")).strip()

        if not match_id:
            continue

        local[match_id] = {
            "prediction": str(row.get("prediction", "")).strip(),
            "score1": str(row.get("score1", "")).strip(),
            "score2": str(row.get("score2", "")).strip(),
        }

    st.session_state.stand_local_predictions = local
    st.session_state.stand_local_user = user_id


def reset_temp_scores():
    st.session_state.temp_score1 = ""
    st.session_state.temp_score2 = ""


def clear_active_score():
    st.session_state.active_match_id = None
    st.session_state.active_prediction = ""
    reset_temp_scores()


def score_display(value):
    shown = value if value else "&nbsp;"
    st.markdown(
        f"""
        <div class="score-display">{shown}</div>
        """,
        unsafe_allow_html=True,
    )


def add_digit(key_name, digit):
    current = st.session_state.get(key_name, "")

    if len(current) < 2:
        st.session_state[key_name] = current + str(digit)


def remove_digit(key_name):
    current = st.session_state.get(key_name, "")
    st.session_state[key_name] = current[:-1]


def numeric_keyboard(label, key_name, unique_prefix):
    st.markdown(f"<div class='keyboard-title'>{label}</div>", unsafe_allow_html=True)

    score_display(st.session_state.get(key_name, ""))

    layout = [
        ["1", "2", "3"],
        ["4", "5", "6"],
        ["7", "8", "9"],
        ["←", "0", "C"],
    ]

    for row_i, row in enumerate(layout):
        cols = st.columns(3)

        for col_i, value in enumerate(row):
            with cols[col_i]:
                if st.button(
                    value,
                    key=f"{unique_prefix}_{key_name}_{row_i}_{col_i}_{value}",
                    use_container_width=True,
                ):
                    if value == "←":
                        remove_digit(key_name)
                    elif value == "C":
                        st.session_state[key_name] = ""
                    else:
                        add_digit(key_name, value)

                    st.rerun()


def prediction_keyboard(match_id, team1, team2):
    st.markdown("<div class='keyboard-title'>Kies uitslag</div>", unsafe_allow_html=True)

    c1, cx, c2 = st.columns(3)

    with c1:
        if st.button("1", key=f"pred_1_{match_id}", use_container_width=True):
            st.session_state.active_match_id = match_id
            st.session_state.active_prediction = "1"
            reset_temp_scores()
            st.rerun()

    with cx:
        if st.button("X", key=f"pred_x_{match_id}", use_container_width=True):
            st.session_state.active_match_id = match_id
            st.session_state.active_prediction = "X"
            reset_temp_scores()
            st.rerun()

    with c2:
        if st.button("2", key=f"pred_2_{match_id}", use_container_width=True):
            st.session_state.active_match_id = match_id
            st.session_state.active_prediction = "2"
            reset_temp_scores()
            st.rerun()


def show_stand_uitprinten(user_id=None):
    st.title("🖨️ Stand uitprinten")

    if user_id is None:
        user_id = st.session_state.get("user", {}).get("naam", "Gast")

    user_id = str(user_id)

    init_local_predictions(user_id)

    matches_df = load_results_matches()

    if matches_df.empty:
        st.warning("Geen wedstrijden gevonden in tabblad 'Matches'.")
        return

    for key, default in {
        "active_match_id": None,
        "active_prediction": "",
        "temp_score1": "",
        "temp_score2": "",
    }.items():
        if key not in st.session_state:
            st.session_state[key] = default

    st.markdown("""
    <style>
    .match-card {
        border: 1px solid rgba(148,163,184,0.45);
        border-radius: 14px;
        padding: 12px;
        margin-bottom: 8px;
        background: rgba(15,23,42,0.35);
    }

    .match-date {
        font-size: 12px;
        color: #94a3b8;
        margin-bottom: 6px;
        font-weight: 700;
    }

    .match-title {
        font-size: 15px;
        font-weight: 900;
        margin-bottom: 8px;
    }

    .score-pill {
        display: inline-block;
        margin-left: 8px;
        padding: 2px 8px;
        border-radius: 999px;
        background: #e0f2fe;
        color: #0f172a;
        font-weight: 900;
        font-size: 12px;
    }

    .keyboard-box {
        border: 1px solid rgba(148,163,184,0.45);
        border-radius: 14px;
        padding: 12px;
        margin-top: 10px;
        margin-bottom: 16px;
        background: rgba(15,23,42,0.55);
    }

    .keyboard-title {
        text-align: center;
        font-size: 13px;
        font-weight: 900;
        color: #cbd5e1;
        margin-bottom: 8px;
    }

    .score-display {
        height: 44px;
        border: 2px solid #cbd5e1;
        border-radius: 10px;
        background: white;
        color: #111827;
        text-align: center;
        font-size: 26px;
        font-weight: 900;
        line-height: 40px;
        margin-bottom: 8px;
    }

    div.stButton > button {
        min-height: 42px;
        font-size: 18px;
        font-weight: 900;
    }

    .bottom-space {
        height: 95px;
    }

    .save-note {
        font-size: 13px;
        color: #94a3b8;
        text-align: center;
        margin-bottom: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.info("Wijzigingen worden pas naar Google Sheets geschreven wanneer je op OPSLAAN drukt.")

    for _, row in matches_df.iterrows():
        match_id = str(row.get("match_id", "")).strip()
        datum_tijd = str(row.get("datum_tijd", "")).strip()
        team1 = str(row.get("team1", "")).strip()
        team2 = str(row.get("team2", "")).strip()

        pred = st.session_state.stand_local_predictions.get(match_id, {})

        prediction = str(pred.get("prediction", "")).strip()
        score1 = str(pred.get("score1", "")).strip()
        score2 = str(pred.get("score2", "")).strip()

        prediction_txt = f'<span class="score-pill">{prediction}</span>' if prediction else ""
        score_txt = f'<span class="score-pill">{score1} - {score2}</span>' if score1 or score2 else ""

        st.markdown(
            f"""
            <div class="match-card">
                <div class="match-date">{datum_tijd}</div>
                <div class="match-title">
                    {team1} vs {team2} {prediction_txt} {score_txt}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        prediction_keyboard(match_id, team1, team2)

        if st.session_state.active_match_id == match_id:
            st.markdown("<div class='keyboard-box'>", unsafe_allow_html=True)

            active_prediction = st.session_state.get("active_prediction", "")

            if active_prediction == "1":
                st.success(f"Gekozen: {team1} wint")
            elif active_prediction == "X":
                st.success("Gekozen: gelijkspel")
            elif active_prediction == "2":
                st.success(f"Gekozen: {team2} wint")

            k1, k2 = st.columns(2)

            with k1:
                numeric_keyboard(team1, "temp_score1", match_id)

            with k2:
                numeric_keyboard(team2, "temp_score2", match_id)

            c_apply, c_cancel = st.columns(2)

            with c_apply:
                if st.button(
                    "✅ Toepassen",
                    key=f"apply_{match_id}",
                    use_container_width=True,
                ):
                    st.session_state.stand_local_predictions[match_id] = {
                        "prediction": active_prediction,
                        "score1": st.session_state.get("temp_score1", ""),
                        "score2": st.session_state.get("temp_score2", ""),
                    }

                    clear_active_score()
                    st.rerun()

            with c_cancel:
                if st.button(
                    "Annuleren",
                    key=f"cancel_{match_id}",
                    use_container_width=True,
                ):
                    clear_active_score()
                    st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="bottom-space"></div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="save-note">Pas bij OPSLAAN wordt alles naar Google Sheets geschreven.</div>',
        unsafe_allow_html=True,
    )

    if st.button("💾 OPSLAAN", type="primary", use_container_width=True):
        save_predictions_to_sheet(
            user_id=user_id,
            local_predictions=st.session_state.stand_local_predictions,
        )
        st.success("Opgeslagen in tabblad 'Predictions'.")
