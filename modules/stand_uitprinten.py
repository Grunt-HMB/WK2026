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
        clean = [str(c).strip() for c in row]

        if "Match No." in clean and "Team 1" in clean and "Team 2" in clean:
            header_row_index = i
            break

    if header_row_index is None:
        st.error("Kon de headerregel in tabblad 'Matches' niet vinden.")
        return empty_df

    headers = [str(c).strip() for c in values[header_row_index]]
    rows = values[header_row_index + 1:]

    fixed_rows = []
    for row in rows:
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
    rows = values[1:]

    fixed_rows = []
    for row in rows:
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
    user_df = predictions_df[predictions_df["user_id"] == str(user_id)].copy()

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


def clear_active():
    st.session_state.active_match_id = None
    st.session_state.active_prediction = ""
    reset_temp_scores()


def add_digit(key_name, digit):
    value = st.session_state.get(key_name, "")

    if len(value) < 2:
        st.session_state[key_name] = value + str(digit)


def remove_digit(key_name):
    value = st.session_state.get(key_name, "")
    st.session_state[key_name] = value[:-1]


def clear_digit(key_name):
    st.session_state[key_name] = ""


def score_box(value):
    shown = value if value else "&nbsp;"

    st.markdown(
        f"""
        <div class="score-box">
            {shown}
        </div>
        """,
        unsafe_allow_html=True,
    )


def numeric_keyboard(label, key_name, prefix):
    st.markdown(f"<div class='kbd-label'>{label}</div>", unsafe_allow_html=True)
    score_box(st.session_state.get(key_name, ""))

    rows = [
        ["1", "2", "3"],
        ["4", "5", "6"],
        ["7", "8", "9"],
        ["←", "0", "C"],
    ]

    for r, row in enumerate(rows):
        cols = st.columns(3, gap="small")

        for c, value in enumerate(row):
            with cols[c]:
                if st.button(
                    value,
                    key=f"{prefix}_{key_name}_{r}_{c}_{value}",
                    use_container_width=True,
                ):
                    if value == "←":
                        remove_digit(key_name)
                    elif value == "C":
                        clear_digit(key_name)
                    else:
                        add_digit(key_name, value)

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
    .block-container {
        padding-left: 0.45rem !important;
        padding-right: 0.45rem !important;
        padding-bottom: 6rem !important;
    }

    .match-card {
        border: 1px solid rgba(148,163,184,0.35);
        border-radius: 12px;
        padding: 9px 10px;
        margin-bottom: 8px;
        background: rgba(15,23,42,0.35);
    }

    .match-top {
        display: flex;
        justify-content: space-between;
        gap: 8px;
        align-items: center;
    }

    .match-date {
        font-size: 11px;
        color: #94a3b8;
        font-weight: 800;
    }

    .match-score {
        font-size: 12px;
        font-weight: 900;
        color: #0f172a;
        background: #e0f2fe;
        border-radius: 999px;
        padding: 2px 8px;
        white-space: nowrap;
    }

    .match-title {
        margin-top: 5px;
        font-size: 14px;
        line-height: 1.2;
        font-weight: 900;
        color: #f8fafc;
    }

    .editor-box {
        border: 1px solid rgba(148,163,184,0.5);
        border-radius: 14px;
        padding: 10px;
        margin: 8px 0 14px 0;
        background: rgba(15,23,42,0.70);
    }

    .editor-title {
        text-align: center;
        font-size: 13px;
        font-weight: 900;
        color: #cbd5e1;
        margin-bottom: 8px;
    }

    .kbd-label {
        text-align: center;
        font-size: 12px;
        font-weight: 900;
        color: #cbd5e1;
        margin-bottom: 4px;
        min-height: 28px;
    }

    .score-box {
        height: 38px;
        border: 2px solid #cbd5e1;
        border-radius: 9px;
        background: white;
        color: #111827;
        text-align: center;
        font-size: 24px;
        font-weight: 900;
        line-height: 34px;
        margin-bottom: 6px;
    }

    div.stButton > button {
        min-height: 34px !important;
        height: 34px !important;
        padding: 0 !important;
        font-size: 15px !important;
        font-weight: 900 !important;
        border-radius: 9px !important;
    }

    .result-row {
        margin-top: -4px;
        margin-bottom: 12px;
    }

    .save-space {
        height: 90px;
    }

    .save-note {
        text-align: center;
        font-size: 12px;
        color: #94a3b8;
        margin: 8px 0;
    }

    @media (max-width: 600px) {
        .main .block-container {
            max-width: 100% !important;
        }

        .match-title {
            font-size: 13px;
        }

        div[data-testid="column"] {
            padding-left: 2px !important;
            padding-right: 2px !important;
        }

        div.stButton > button {
            font-size: 14px !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    st.info("Kies 1/X/2, vul de score in en klik Toepassen. Pas daarna OPSLAAN schrijft naar Google Sheets.")

    for _, row in matches_df.iterrows():
        match_id = str(row.get("match_id", "")).strip()
        datum_tijd = str(row.get("datum_tijd", "")).strip()
        team1 = str(row.get("team1", "")).strip()
        team2 = str(row.get("team2", "")).strip()

        pred = st.session_state.stand_local_predictions.get(match_id, {})

        prediction = str(pred.get("prediction", "")).strip()
        score1 = str(pred.get("score1", "")).strip()
        score2 = str(pred.get("score2", "")).strip()

        score_text = ""
        if prediction or score1 or score2:
            score_text = f"{prediction} · {score1}-{score2}".strip(" ·-")

        score_html = ""
        if score_text:
            score_html = f"<div class='match-score'>{score_text}</div>"

        st.markdown(
            f"""
            <div class="match-card">
                <div class="match-top">
                    <div class="match-date">{datum_tijd}</div>
                    {score_html}
                </div>
                <div class="match-title">{team1} vs {team2}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        c1, cx, c2 = st.columns(3, gap="small")

        with c1:
            if st.button("1", key=f"pick_1_{match_id}", use_container_width=True):
                st.session_state.active_match_id = match_id
                st.session_state.active_prediction = "1"
                reset_temp_scores()
                st.rerun()

        with cx:
            if st.button("X", key=f"pick_x_{match_id}", use_container_width=True):
                st.session_state.active_match_id = match_id
                st.session_state.active_prediction = "X"
                reset_temp_scores()
                st.rerun()

        with c2:
            if st.button("2", key=f"pick_2_{match_id}", use_container_width=True):
                st.session_state.active_match_id = match_id
                st.session_state.active_prediction = "2"
                reset_temp_scores()
                st.rerun()

        if st.session_state.active_match_id == match_id:
            st.markdown("<div class='editor-box'>", unsafe_allow_html=True)

            active_prediction = st.session_state.get("active_prediction", "")

            if active_prediction == "1":
                msg = f"{team1} wint"
            elif active_prediction == "X":
                msg = "Gelijkspel"
            elif active_prediction == "2":
                msg = f"{team2} wint"
            else:
                msg = ""

            st.markdown(
                f"<div class='editor-title'>Gekozen: {msg}</div>",
                unsafe_allow_html=True,
            )

            k1, k2 = st.columns(2, gap="small")

            with k1:
                numeric_keyboard(team1, "temp_score1", match_id)

            with k2:
                numeric_keyboard(team2, "temp_score2", match_id)

            a, b = st.columns(2, gap="small")

            with a:
                if st.button("✅ Toepassen", key=f"apply_{match_id}", use_container_width=True):
                    st.session_state.stand_local_predictions[match_id] = {
                        "prediction": active_prediction,
                        "score1": st.session_state.get("temp_score1", ""),
                        "score2": st.session_state.get("temp_score2", ""),
                    }

                    clear_active()
                    st.rerun()

            with b:
                if st.button("Annuleren", key=f"cancel_{match_id}", use_container_width=True):
                    clear_active()
                    st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="save-space"></div>', unsafe_allow_html=True)
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
