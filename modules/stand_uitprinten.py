import json
from datetime import datetime

import gspread
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from google.oauth2.service_account import Credentials


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


def get_query_value(name, default=""):
    value = st.query_params.get(name, default)

    if isinstance(value, list):
        return value[0] if value else default

    return value


def process_query_actions(user_id):
    action = get_query_value("stand_action", "")

    if not action:
        return

    if action == "save_payload":
        payload = get_query_value("payload", "")

        try:
            matches = json.loads(payload)
        except Exception:
            matches = []

        local = {}

        for item in matches:
            match_id = str(item.get("match_id", "")).strip()
            prediction = str(item.get("prediction", "")).strip()
            score1 = str(item.get("score1", "")).strip()
            score2 = str(item.get("score2", "")).strip()

            if not match_id:
                continue

            if prediction == "" and score1 == "" and score2 == "":
                continue

            local[match_id] = {
                "prediction": prediction,
                "score1": score1,
                "score2": score2,
            }

        st.session_state.stand_local_predictions = local

        save_predictions_to_sheet(
            user_id=user_id,
            local_predictions=st.session_state.stand_local_predictions,
        )

        st.session_state.stand_message = "Opgeslagen in tabblad 'Predictions'."

    st.query_params.clear()
    st.session_state.main_page = "🖨️ Stand uitprinten"
    st.rerun()


def build_mobile_html(matches_df, local_predictions):
    matches = []

    for _, row in matches_df.iterrows():
        match_id = str(row.get("match_id", "")).strip()
        datum_tijd = str(row.get("datum_tijd", "")).strip()
        team1 = str(row.get("team1", "")).strip()
        team2 = str(row.get("team2", "")).strip()

        pred = local_predictions.get(match_id, {})

        matches.append({
            "match_id": match_id,
            "datum_tijd": datum_tijd,
            "team1": team1,
            "team2": team2,
            "prediction": str(pred.get("prediction", "")).strip(),
            "score1": str(pred.get("score1", "")).strip(),
            "score2": str(pred.get("score2", "")).strip(),
        })

    matches_json = json.dumps(matches, ensure_ascii=False)

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">

        <style>
            * {{
                box-sizing: border-box;
                -webkit-tap-highlight-color: transparent;
            }}

            body {{
                margin: 0;
                padding: 0 0 80px 0;
                font-family: Arial, sans-serif;
                color: #f8fafc;
                background: transparent;
            }}

            .info {{
                background: rgba(30, 64, 175, 0.22);
                border: 1px solid rgba(147, 197, 253, 0.35);
                color: #dbeafe;
                padding: 10px 12px;
                border-radius: 12px;
                font-size: 13px;
                margin-bottom: 10px;
            }}

            .match-card {{
                background: rgba(15, 23, 42, 0.70);
                border: 1px solid rgba(148, 163, 184, 0.35);
                border-radius: 14px;
                padding: 10px;
                margin-bottom: 9px;
            }}

            .match-top {{
                display: flex;
                justify-content: space-between;
                gap: 8px;
                align-items: center;
                margin-bottom: 6px;
            }}

            .date {{
                font-size: 11px;
                color: #94a3b8;
                font-weight: 700;
            }}

            .badge {{
                background: #e0f2fe;
                color: #0f172a;
                padding: 3px 8px;
                border-radius: 999px;
                font-size: 11px;
                font-weight: 900;
                white-space: nowrap;
            }}

            .teams {{
                font-size: 14px;
                font-weight: 900;
                line-height: 1.25;
                margin-bottom: 9px;
            }}

            .pick-row {{
                display: grid;
                grid-template-columns: 1fr 1fr 1fr;
                gap: 6px;
            }}

            .pick-btn {{
                height: 38px;
                border: 0;
                border-radius: 10px;
                font-size: 16px;
                font-weight: 900;
                background: #f1f5f9;
                color: #0f172a;
                cursor: pointer;
            }}

            .pick-btn:active,
            .key:active,
            .apply-btn:active,
            .cancel-btn:active,
            .save-btn:active {{
                transform: scale(0.97);
            }}

            .editor {{
                display: none;
                margin-top: 10px;
                padding: 10px;
                border-radius: 14px;
                background: #0f172a;
                border: 1px solid rgba(148, 163, 184, 0.45);
            }}

            .editor-title {{
                text-align: center;
                font-size: 14px;
                font-weight: 900;
                margin-bottom: 4px;
            }}

            .editor-subtitle {{
                text-align: center;
                font-size: 12px;
                color: #94a3b8;
                margin-bottom: 10px;
            }}

            .score-row {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 8px;
            }}

            .score-panel {{
                background: rgba(30, 41, 59, 0.9);
                border-radius: 13px;
                padding: 7px;
            }}

            .team-label {{
                text-align: center;
                font-size: 11px;
                font-weight: 900;
                color: #cbd5e1;
                min-height: 28px;
                margin-bottom: 4px;
                line-height: 1.2;
            }}

            .score-display {{
                height: 40px;
                background: white;
                color: #0f172a;
                border-radius: 10px;
                text-align: center;
                font-size: 25px;
                font-weight: 900;
                line-height: 40px;
                margin-bottom: 7px;
            }}

            .keypad {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 5px;
            }}

            .key {{
                height: 32px;
                border: 0;
                border-radius: 8px;
                background: #f8fafc;
                color: #0f172a;
                font-size: 14px;
                font-weight: 900;
                cursor: pointer;
            }}

            .key.special {{
                background: #cbd5e1;
            }}

            .action-row {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 8px;
                margin-top: 10px;
            }}

            .apply-btn,
            .cancel-btn {{
                height: 40px;
                border: 0;
                border-radius: 12px;
                font-size: 14px;
                font-weight: 900;
                cursor: pointer;
            }}

            .apply-btn {{
                background: #22c55e;
                color: #052e16;
            }}

            .cancel-btn {{
                background: #334155;
                color: #f8fafc;
            }}

            .save-bar {{
                position: fixed;
                left: 0;
                right: 0;
                bottom: 0;
                z-index: 1000;
                padding: 10px;
                background: rgba(15, 23, 42, 0.97);
                border-top: 1px solid rgba(255,255,255,0.14);
            }}

            .save-btn {{
                width: 100%;
                height: 48px;
                border: 0;
                border-radius: 14px;
                background: #2563eb;
                color: white;
                font-size: 17px;
                font-weight: 900;
                cursor: pointer;
            }}
        </style>
    </head>

    <body>
        <div class="info">
            Kies 1 / X / 2. Vul de score in. <b>Toepassen</b> werkt zonder refresh.
            Pas bij <b>OPSLAAN</b> wordt Google Sheets aangepast.
        </div>

        <div id="matches"></div>

        <div class="save-bar">
            <button class="save-btn" onclick="saveAll()">💾 OPSLAAN</button>
        </div>

        <script>
            const matches = {matches_json};

            let activeMatch = null;
            let activePrediction = "";
            let tempScore1 = "";
            let tempScore2 = "";

            function escapeHtml(text) {{
                return String(text || "")
                    .replaceAll("&", "&amp;")
                    .replaceAll("<", "&lt;")
                    .replaceAll(">", "&gt;")
                    .replaceAll('"', "&quot;")
                    .replaceAll("'", "&#039;");
            }}

            function renderMatches() {{
                const wrap = document.getElementById("matches");
                let output = "";

                matches.forEach(m => {{
                    let badge = "";

                    if (m.prediction || m.score1 || m.score2) {{
                        let parts = [];

                        if (m.prediction) {{
                            parts.push(m.prediction);
                        }}

                        if (m.score1 || m.score2) {{
                            parts.push((m.score1 || "") + "-" + (m.score2 || ""));
                        }}

                        badge = `<div class="badge">${{escapeHtml(parts.join(" · "))}}</div>`;
                    }}

                    output += `
                        <div class="match-card" id="card-${{escapeHtml(m.match_id)}}">
                            <div class="match-top">
                                <div class="date">${{escapeHtml(m.datum_tijd)}}</div>
                                ${{badge}}
                            </div>

                            <div class="teams">
                                ${{escapeHtml(m.team1)}} vs ${{escapeHtml(m.team2)}}
                            </div>

                            <div class="pick-row">
                                <button class="pick-btn" onclick="openEditor('${{escapeHtml(m.match_id)}}', '1')">1</button>
                                <button class="pick-btn" onclick="openEditor('${{escapeHtml(m.match_id)}}', 'X')">X</button>
                                <button class="pick-btn" onclick="openEditor('${{escapeHtml(m.match_id)}}', '2')">2</button>
                            </div>

                            <div class="editor" id="editor-${{escapeHtml(m.match_id)}}"></div>
                        </div>
                    `;
                }});

                wrap.innerHTML = output;
            }}

            function findMatch(matchId) {{
                return matches.find(m => String(m.match_id) === String(matchId));
            }}

            function openEditor(matchId, prediction) {{
                document.querySelectorAll(".editor").forEach(e => {{
                    e.style.display = "none";
                    e.innerHTML = "";
                }});

                activeMatch = findMatch(matchId);
                activePrediction = prediction;

                tempScore1 = "";
                tempScore2 = "";

                if (!activeMatch) return;

                let choiceText = "";

                if (prediction === "1") choiceText = activeMatch.team1 + " wint";
                if (prediction === "X") choiceText = "Gelijkspel";
                if (prediction === "2") choiceText = activeMatch.team2 + " wint";

                const editor = document.getElementById("editor-" + matchId);

                editor.innerHTML = `
                    <div class="editor-title">${{escapeHtml(activeMatch.team1)}} vs ${{escapeHtml(activeMatch.team2)}}</div>
                    <div class="editor-subtitle">Gekozen: ${{escapeHtml(choiceText)}}</div>

                    <div class="score-row">
                        <div class="score-panel">
                            <div class="team-label">${{escapeHtml(activeMatch.team1)}}</div>
                            <div class="score-display" id="score1">&nbsp;</div>
                            <div class="keypad" id="keypad1"></div>
                        </div>

                        <div class="score-panel">
                            <div class="team-label">${{escapeHtml(activeMatch.team2)}}</div>
                            <div class="score-display" id="score2">&nbsp;</div>
                            <div class="keypad" id="keypad2"></div>
                        </div>
                    </div>

                    <div class="action-row">
                        <button class="apply-btn" onclick="applyScore()">✅ Toepassen</button>
                        <button class="cancel-btn" onclick="closeEditor('${{escapeHtml(matchId)}}')">Annuleren</button>
                    </div>
                `;

                editor.style.display = "block";
                buildKeypads();
                updateDisplays();

                setTimeout(() => {{
                    editor.scrollIntoView({{ behavior: "smooth", block: "center" }});
                }}, 50);
            }}

            function closeEditor(matchId) {{
                const editor = document.getElementById("editor-" + matchId);

                if (editor) {{
                    editor.style.display = "none";
                    editor.innerHTML = "";
                }}

                activeMatch = null;
                activePrediction = "";
                tempScore1 = "";
                tempScore2 = "";
            }}

            function updateDisplays() {{
                const s1 = document.getElementById("score1");
                const s2 = document.getElementById("score2");

                if (s1) s1.innerHTML = tempScore1 || "&nbsp;";
                if (s2) s2.innerHTML = tempScore2 || "&nbsp;";
            }}

            function addDigit(side, digit) {{
                if (side === 1) {{
                    if (tempScore1.length < 2) tempScore1 += digit;
                }} else {{
                    if (tempScore2.length < 2) tempScore2 += digit;
                }}

                updateDisplays();
            }}

            function backspace(side) {{
                if (side === 1) {{
                    tempScore1 = tempScore1.slice(0, -1);
                }} else {{
                    tempScore2 = tempScore2.slice(0, -1);
                }}

                updateDisplays();
            }}

            function clearScore(side) {{
                if (side === 1) {{
                    tempScore1 = "";
                }} else {{
                    tempScore2 = "";
                }}

                updateDisplays();
            }}

            function buildOneKeypad(side) {{
                const nums = ["1","2","3","4","5","6","7","8","9"];
                let output = "";

                nums.forEach(n => {{
                    output += `<button class="key" onclick="addDigit(${{side}}, '${{n}}')">${{n}}</button>`;
                }});

                output += `<button class="key special" onclick="backspace(${{side}})">←</button>`;
                output += `<button class="key" onclick="addDigit(${{side}}, '0')">0</button>`;
                output += `<button class="key special" onclick="clearScore(${{side}})">C</button>`;

                return output;
            }}

            function buildKeypads() {{
                document.getElementById("keypad1").innerHTML = buildOneKeypad(1);
                document.getElementById("keypad2").innerHTML = buildOneKeypad(2);
            }}

            function applyScore() {{
                if (!activeMatch) return;

                activeMatch.prediction = activePrediction;
                activeMatch.score1 = tempScore1;
                activeMatch.score2 = tempScore2;

                const rememberId = activeMatch.match_id;

                activeMatch = null;
                activePrediction = "";
                tempScore1 = "";
                tempScore2 = "";

                renderMatches();

                setTimeout(() => {{
                    const card = document.getElementById("card-" + rememberId);
                    if (card) {{
                        card.scrollIntoView({{ behavior: "smooth", block: "center" }});
                    }}
                }}, 50);
            }}

            function goWithParams(params) {{
                const query = new URLSearchParams(params).toString();

                try {{
                    const base = window.parent.location.pathname;
                    window.parent.location.href = base + "?" + query;
                }} catch(e) {{
                    window.location.href = "?" + query;
                }}
            }}

            function saveAll() {{
                const changed = matches.filter(m => {{
                    return m.prediction || m.score1 || m.score2;
                }});

                const payload = JSON.stringify(changed);

                goWithParams({{
                    stand_action: "save_payload",
                    payload: payload
                }});
            }}

            renderMatches();
        </script>
    </body>
    </html>
    """


def show_stand_uitprinten(user_id=None):
    st.title("🖨️ Stand uitprinten")

    if user_id is None:
        user_id = st.session_state.get("user", {}).get("naam", "Gast")

    user_id = str(user_id)

    init_local_predictions(user_id)
    process_query_actions(user_id)

    if "stand_message" in st.session_state:
        st.success(st.session_state.stand_message)
        del st.session_state.stand_message

    matches_df = load_results_matches()

    if matches_df.empty:
        st.warning("Geen wedstrijden gevonden in tabblad 'Matches'.")
        return

    html_code = build_mobile_html(
        matches_df=matches_df,
        local_predictions=st.session_state.stand_local_predictions,
    )

    height = max(850, 126 * len(matches_df) + 180)

    components.html(
        html_code,
        height=height,
        scrolling=False,
    )
