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

        if (
            "Match No." in clean_row
            and "Team 1" in clean_row
            and "Team 2" in clean_row
        ):
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

    if "Date (my time)" in raw_df.columns:
        date_col = "Date (my time)"
    elif "Date  (my time)" in raw_df.columns:
        date_col = "Date  (my time)"
    else:
        date_col = ""

    df = pd.DataFrame()
    df["match_id"] = raw_df["Match No."].astype(str).str.strip()
    df["team1"] = raw_df["Team 1"].astype(str).str.strip()
    df["team2"] = raw_df["Team 2"].astype(str).str.strip()

    if date_col:
        df["datum_tijd"] = raw_df[date_col].astype(str).str.strip()
    else:
        df["datum_tijd"] = ""

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

    df = df[
        (df["user_id"] != "")
        & (df["match_id"] != "")
    ].copy()

    return df


def save_predictions_to_sheet(user_id, local_predictions):
    sh = connect_results_sheet()
    ws = sh.worksheet(PREDICTIONS_SHEET)

    existing_df = load_results_predictions()

    if existing_df.empty:
        existing_df = pd.DataFrame(columns=PREDICTION_HEADERS)

    existing_df["user_id"] = existing_df["user_id"].astype(str).str.strip()
    existing_df["match_id"] = existing_df["match_id"].astype(str).str.strip()

    rows_to_keep = existing_df[
        existing_df["user_id"] != str(user_id)
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


def clear_active_score():
    st.session_state.active_match_id = None
    st.session_state.active_prediction = ""
    st.session_state.temp_score1 = ""
    st.session_state.temp_score2 = ""


def digit_keyboard(label, key_prefix):
    st.markdown(f"**{label}**")

    if key_prefix not in st.session_state:
        st.session_state[key_prefix] = ""

    cols = st.columns(3)

    digits = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]

    for i, digit in enumerate(digits):
        with cols[i % 3]:
            if st.button(
                digit,
                key=f"{key_prefix}_{digit}",
                use_container_width=True,
            ):
                if len(st.session_state[key_prefix]) < 2:
                    st.session_state[key_prefix] += digit
                st.rerun()

    col_back, col_zero, _ = st.columns(3)

    with col_back:
        if st.button(
            "←",
            key=f"{key_prefix}_back",
            use_container_width=True,
        ):
            st.session_state[key_prefix] = st.session_state[key_prefix][:-1]
            st.rerun()

    with col_zero:
        if st.button(
            "0",
            key=f"{key_prefix}_0",
            use_container_width=True,
        ):
            if len(st.session_state[key_prefix]) < 2:
                st.session_state[key_prefix] += "0"
            st.rerun()

    value = st.session_state[key_prefix] or "&nbsp;"

    st.markdown(
        f"""
        <div style="
            margin-top:8px;
            padding:8px;
            border:1px solid #cbd5e1;
            border-radius:8px;
            text-align:center;
            font-size:24px;
            font-weight:900;
            background:white;
            color:#111827;
        ">
            {value}
        </div>
        """,
        unsafe_allow_html=True,
    )


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

    if "active_match_id" not in st.session_state:
        st.session_state.active_match_id = None

    if "active_prediction" not in st.session_state:
        st.session_state.active_prediction = ""

    if "temp_score1" not in st.session_state:
        st.session_state.temp_score1 = ""

    if "temp_score2" not in st.session_state:
        st.session_state.temp_score2 = ""

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

    .bottom-space {
        height: 90px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.info(
        "Wijzigingen worden pas naar Google Sheets geschreven wanneer je op OPSLAAN drukt."
    )

    for _, row in matches_df.iterrows():
        match_id = str(row.get("match_id", "")).strip()
        datum_tijd = str(row.get("datum_tijd", "")).strip()
        team1 = str(row.get("team1", "")).strip()
        team2 = str(row.get("team2", "")).strip()

        pred = st.session_state.stand_local_predictions.get(match_id, {})

        prediction = str(pred.get("prediction", "")).strip()
        score1 = str(pred.get("score1", "")).strip()
        score2 = str(pred.get("score2", "")).strip()

        score_txt = ""

        if score1 != "" or score2 != "":
            score_txt = f'<span class="score-pill">{score1} - {score2}</span>'

        prediction_txt = ""

        if prediction:
            prediction_txt = f'<span class="score-pill">{prediction}</span>'

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

        col1, colx, col2 = st.columns(3)

        with col1:
            if st.button(
                "1",
                key=f"pred_1_{match_id}",
                use_container_width=True,
            ):
                st.session_state.active_match_id = match_id
                st.session_state.active_prediction = "1"
                st.session_state.temp_score1 = ""
                st.session_state.temp_score2 = ""
                st.rerun()

        with colx:
            if st.button(
                "X",
                key=f"pred_x_{match_id}",
                use_container_width=True,
            ):
                st.session_state.active_match_id = match_id
                st.session_state.active_prediction = "X"
                st.session_state.temp_score1 = ""
                st.session_state.temp_score2 = ""
                st.rerun()

        with col2:
            if st.button(
                "2",
                key=f"pred_2_{match_id}",
                use_container_width=True,
            ):
                st.session_state.active_match_id = match_id
                st.session_state.active_prediction = "2"
                st.session_state.temp_score1 = ""
                st.session_state.temp_score2 = ""
                st.rerun()

        if st.session_state.active_match_id == match_id:
            st.markdown("---")
            st.markdown(f"### Score voor: {team1} vs {team2}")

            active_prediction = st.session_state.get("active_prediction", "")

            if active_prediction == "1":
                st.success(f"Gekozen: {team1} wint")
            elif active_prediction == "X":
                st.success("Gekozen: gelijkspel")
            elif active_prediction == "2":
                st.success(f"Gekozen: {team2} wint")

            k1, k2 = st.columns(2)

            with k1:
                digit_keyboard(team1, "temp_score1")

            with k2:
                digit_keyboard(team2, "temp_score2")

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

            st.markdown("---")

    st.markdown('<div class="bottom-space"></div>', unsafe_allow_html=True)

    if st.button("💾 OPSLAAN", type="primary", use_container_width=True):
        save_predictions_to_sheet(
            user_id=user_id,
            local_predictions=st.session_state.stand_local_predictions,
        )
        st.success("Opgeslagen in tabblad 'Predictions'.")
