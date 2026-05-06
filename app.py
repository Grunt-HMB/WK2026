import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime


# =========================
# CONFIG
# =========================

st.set_page_config(
    page_title="WK 2026 Pronostiek",
    page_icon="⚽",
    layout="wide"
)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]


# =========================
# GOOGLE SHEETS
# =========================

@st.cache_resource
def connect_to_gsheet():
    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES
    )

    client = gspread.authorize(credentials)
    sheet_id = st.secrets["GOOGLE_SHEET_ID"]
    return client.open_by_key(sheet_id)


def get_worksheet(name):
    sh = connect_to_gsheet()
    return sh.worksheet(name)


def load_sheet(name):
    ws = get_worksheet(name)
    data = ws.get_all_records()
    return pd.DataFrame(data)


def append_row(sheet_name, row):
    ws = get_worksheet(sheet_name)
    ws.append_row(row, value_input_option="USER_ENTERED")


def update_or_append_prediction(user_id, match_id, pred_team1, pred_team2):
    ws = get_worksheet("Predictions")
    rows = ws.get_all_values()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for index, row in enumerate(rows[1:], start=2):
        if str(row[0]) == str(user_id) and str(row[1]) == str(match_id):
            ws.update(
                f"C{index}:E{index}",
                [[pred_team1, pred_team2, timestamp]]
            )
            return

    append_row("Predictions", [
        user_id,
        match_id,
        pred_team1,
        pred_team2,
        timestamp
    ])


def update_or_append_result(match_id, real_team1, real_team2):
    ws = get_worksheet("Results")
    rows = ws.get_all_values()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for index, row in enumerate(rows[1:], start=2):
        if str(row[0]) == str(match_id):
            ws.update(
                f"B{index}:D{index}",
                [[real_team1, real_team2, timestamp]]
            )
            return

    append_row("Results", [
        match_id,
        real_team1,
        real_team2,
        timestamp
    ])


# =========================
# HELPERS
# =========================

def safe_int(value):
    try:
        return int(value)
    except:
        return None


def get_match_result_type(score1, score2):
    if score1 > score2:
        return "team1"
    elif score2 > score1:
        return "team2"
    else:
        return "draw"


def calculate_points(pred1, pred2, real1, real2):
    pred1 = safe_int(pred1)
    pred2 = safe_int(pred2)
    real1 = safe_int(real1)
    real2 = safe_int(real2)

    if pred1 is None or pred2 is None or real1 is None or real2 is None:
        return 0

    points = 0

    pred_type = get_match_result_type(pred1, pred2)
    real_type = get_match_result_type(real1, real2)

    if pred_type == real_type:
        points += 3

    if pred1 == real1 and pred2 == real2:
        points += 2

    pred_diff = pred1 - pred2
    real_diff = real1 - real2

    if pred_diff == real_diff and not (pred1 == real1 and pred2 == real2):
        points += 1

    return points


def login(users_df):
    st.sidebar.title("Login")

    naam = st.sidebar.text_input("Naam")
    pincode = st.sidebar.text_input("Pincode", type="password")

    if st.sidebar.button("Inloggen"):
        user = users_df[
            (users_df["naam"].astype(str).str.lower() == naam.lower()) &
            (users_df["pincode"].astype(str) == str(pincode))
        ]

        if user.empty:
            st.sidebar.error("Naam of pincode is fout.")
        else:
            st.session_state["user"] = user.iloc[0].to_dict()
            st.sidebar.success("Ingelogd.")

    return st.session_state.get("user")


# =========================
# DATA LADEN
# =========================

try:
    users_df = load_sheet("Users")
    matches_df = load_sheet("Matches")
    predictions_df = load_sheet("Predictions")
    results_df = load_sheet("Results")
except Exception as e:
    st.error("Fout bij laden van Google Sheets.")
    st.exception(e)
    st.stop()


# =========================
# LOGIN
# =========================

st.title("⚽ WK 2026 Pronostiek")

user = login(users_df)

if not user:
    st.info("Log in via de zijbalk.")
    st.stop()

user_id = str(user["user_id"])
is_admin = str(user.get("admin", "")).upper() == "TRUE"

st.sidebar.markdown("---")
st.sidebar.write(f"Ingelogd als: **{user['naam']}**")

menu_options = ["Voorspellingen invullen", "Scorebord"]

if is_admin:
    menu_options.append("Admin - Uitslagen invullen")

menu = st.sidebar.radio("Menu", menu_options)


# =========================
# VOORSPELLINGEN
# =========================

if menu == "Voorspellingen invullen":
    st.header("Voorspellingen invullen")

    speeldagen = sorted(matches_df["speeldag"].dropna().unique())
    selected_speeldag = st.selectbox("Kies speeldag", speeldagen)

    day_matches = matches_df[matches_df["speeldag"] == selected_speeldag]

    user_predictions = predictions_df[
        predictions_df["user_id"].astype(str) == user_id
    ] if not predictions_df.empty else pd.DataFrame()

    for _, match in day_matches.iterrows():
        match_id = str(match["match_id"])

        existing = user_predictions[
            user_predictions["match_id"].astype(str) == match_id
        ] if not user_predictions.empty else pd.DataFrame()

        default1 = 0
        default2 = 0

        if not existing.empty:
            default1 = safe_int(existing.iloc[0]["pred_team1"]) or 0
            default2 = safe_int(existing.iloc[0]["pred_team2"]) or 0

        with st.container(border=True):
            st.subheader(f"{match['team1']} - {match['team2']}")
            st.caption(f"Speeldag {match['speeldag']} | {match['ronde']} | Groep {match['groep']} | {match['datum']}")

            col1, col2, col3 = st.columns([2, 1, 2])

            with col1:
                pred1 = st.number_input(
                    f"Goals {match['team1']}",
                    min_value=0,
                    max_value=20,
                    value=default1,
                    step=1,
                    key=f"pred1_{match_id}"
                )

            with col2:
                st.markdown("### -")

            with col3:
                pred2 = st.number_input(
                    f"Goals {match['team2']}",
                    min_value=0,
                    max_value=20,
                    value=default2,
                    step=1,
                    key=f"pred2_{match_id}"
                )

            if st.button("Opslaan", key=f"save_pred_{match_id}"):
                update_or_append_prediction(user_id, match_id, pred1, pred2)
                st.success("Voorspelling opgeslagen.")
                st.cache_data.clear()
                st.rerun()


# =========================
# ADMIN RESULTATEN
# =========================

elif menu == "Admin - Uitslagen invullen":
    st.header("Admin - echte uitslagen invullen")

    speeldagen = sorted(matches_df["speeldag"].dropna().unique())
    selected_speeldag = st.selectbox("Kies speeldag", speeldagen)

    day_matches = matches_df[matches_df["speeldag"] == selected_speeldag]

    for _, match in day_matches.iterrows():
        match_id = str(match["match_id"])

        existing = results_df[
            results_df["match_id"].astype(str) == match_id
        ] if not results_df.empty else pd.DataFrame()

        default1 = 0
        default2 = 0

        if not existing.empty:
            default1 = safe_int(existing.iloc[0]["real_team1"]) or 0
            default2 = safe_int(existing.iloc[0]["real_team2"]) or 0

        with st.container(border=True):
            st.subheader(f"{match['team1']} - {match['team2']}")
            st.caption(f"Match ID: {match_id}")

            col1, col2, col3 = st.columns([2, 1, 2])

            with col1:
                real1 = st.number_input(
                    f"Echte goals {match['team1']}",
                    min_value=0,
                    max_value=20,
                    value=default1,
                    step=1,
                    key=f"real1_{match_id}"
                )

            with col2:
                st.markdown("### -")

            with col3:
                real2 = st.number_input(
                    f"Echte goals {match['team2']}",
                    min_value=0,
                    max_value=20,
                    value=default2,
                    step=1,
                    key=f"real2_{match_id}"
                )

            if st.button("Uitslag opslaan", key=f"save_result_{match_id}"):
                update_or_append_result(match_id, real1, real2)
                st.success("Uitslag opgeslagen.")
                st.cache_data.clear()
                st.rerun()


# =========================
# SCOREBORD
# =========================

elif menu == "Scorebord":
    st.header("Scorebord")

    if predictions_df.empty or results_df.empty:
        st.info("Nog niet genoeg voorspellingen of uitslagen.")
        st.stop()

    merged = predictions_df.merge(
        results_df,
        on="match_id",
        how="inner"
    )

    merged = merged.merge(
        matches_df,
        on="match_id",
        how="left"
    )

    merged = merged.merge(
        users_df[["user_id", "naam"]],
        on="user_id",
        how="left"
    )

    merged["punten"] = merged.apply(
        lambda row: calculate_points(
            row["pred_team1"],
            row["pred_team2"],
            row["real_team1"],
            row["real_team2"]
        ),
        axis=1
    )

    speeldagen = ["Alle"] + sorted(merged["speeldag"].dropna().unique().tolist())
    selected_speeldag = st.selectbox("Scorebord per speeldag", speeldagen)

    if selected_speeldag != "Alle":
        merged_view = merged[merged["speeldag"] == selected_speeldag]
    else:
        merged_view = merged.copy()

    scoreboard = (
        merged_view
        .groupby("naam", as_index=False)
        .agg(
            totaal_punten=("punten", "sum"),
            wedstrijden=("match_id", "count")
        )
        .sort_values("totaal_punten", ascending=False)
    )

    st.subheader("Klassement")
    st.dataframe(scoreboard, use_container_width=True, hide_index=True)

    st.subheader("Detail per wedstrijd")

    detail_cols = [
        "naam",
        "speeldag",
        "team1",
        "team2",
        "pred_team1",
        "pred_team2",
        "real_team1",
        "real_team2",
        "punten"
    ]

    st.dataframe(
        merged_view[detail_cols].sort_values(["speeldag", "naam"]),
        use_container_width=True,
        hide_index=True
    )
