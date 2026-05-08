import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from modules.settings import REQUIRED_SHEETS
from modules.utils import timestamp

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

@st.cache_resource
def connect_to_gsheet():
    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES,
    )
    client = gspread.authorize(credentials)
    sheet_id = st.secrets["GOOGLE_SHEET_ID"]
    return client.open_by_key(sheet_id)

def get_worksheet(name):
    sh = connect_to_gsheet()
    return sh.worksheet(name)

def ensure_sheets_exist():
    sh = connect_to_gsheet()
    existing = [ws.title for ws in sh.worksheets()]
    missing = [name for name in REQUIRED_SHEETS.keys() if name not in existing]

    if missing:
        st.error("Deze tabbladen ontbreken in Google Sheets: " + ", ".join(missing))
        st.stop()

def load_sheet(name):
    ws = get_worksheet(name)
    data = ws.get_all_records()
    df = pd.DataFrame(data)

    for col in REQUIRED_SHEETS.get(name, []):
        if col not in df.columns:
            df[col] = ""

    return df

def load_all_data():
    return {
        "users": load_sheet("Users"),
        "matches": load_sheet("Matches"),
        "predictions": load_sheet("Predictions"),
        "results": load_sheet("Results"),
    }

def append_row(sheet_name, row):
    ws = get_worksheet(sheet_name)
    ws.append_row(row, value_input_option="USER_ENTERED")

def get_next_user_id(users_df):
    if users_df.empty:
        return 1

    ids = []
    for value in users_df["user_id"].tolist():
        try:
            ids.append(int(value))
        except Exception:
            pass

    return max(ids) + 1 if ids else 1

def batch_upsert_predictions(user_id, local_predictions, status):
    """
    local_predictions:
    {
        "1": {"prediction": "1", "score1": "", "score2": ""},
        "2": {"prediction": "X", "score1": 1, "score2": 1}
    }
    """
    if not local_predictions:
        return 0

    ws = get_worksheet("Predictions")
    rows = ws.get_all_values()

    if not rows:
        ws.append_row(REQUIRED_SHEETS["Predictions"], value_input_option="USER_ENTERED")
        rows = ws.get_all_values()

    existing_map = {}
    for row_index, row in enumerate(rows[1:], start=2):
        if len(row) >= 2:
            existing_map[(str(row[0]), str(row[1]))] = row_index

    now = timestamp()
    updates = []
    appends = []

    for match_id, data in local_predictions.items():
        prediction = data.get("prediction", "")
        score1 = data.get("score1", "")
        score2 = data.get("score2", "")

        key = (str(user_id), str(match_id))

        if key in existing_map:
            row_index = existing_map[key]
            updates.append({
                "range": f"C{row_index}:G{row_index}",
                "values": [[prediction, score1, score2, status, now]],
            })
        else:
            appends.append([user_id, match_id, prediction, score1, score2, status, now])

    if updates:
        ws.batch_update(updates, value_input_option="USER_ENTERED")

    if appends:
        ws.append_rows(appends, value_input_option="USER_ENTERED")

    return len(local_predictions)

def update_or_append_result(match_id, real_team1, real_team2):
    ws = get_worksheet("Results")
    rows = ws.get_all_values()

    if not rows:
        ws.append_row(REQUIRED_SHEETS["Results"], value_input_option="USER_ENTERED")
        rows = ws.get_all_values()

    now = timestamp()

    for index, row in enumerate(rows[1:], start=2):
        if len(row) >= 1 and str(row[0]) == str(match_id):
            ws.update(f"B{index}:D{index}", [[real_team1, real_team2, now]])
            return

    ws.append_row([match_id, real_team1, real_team2, now], value_input_option="USER_ENTERED")
