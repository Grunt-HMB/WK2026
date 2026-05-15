import re
import streamlit as st

from modules.database import (
    load_matches,
    load_predictions,
    batch_save_predictions,
)


def show_pronostiek_scores(user_id="Tom"):

    def country_flag(code):
        code = str(code or "").strip().upper()
        if len(code) != 2:
            return "⚽"
        return chr(ord(code[0]) + 127397) + chr(ord(code[1]) + 127397)

    def format_date(value):
        txt = str(value or "").strip()
        parts = txt.split("-")
        if len(parts) >= 2:
            return f"{parts[0]}/{parts[1]}"
        return txt

    def format_time(value):
        txt = str(value or "").strip()
        if txt.count(":") >= 2:
            return ":".join(txt.split(":")[:2])
        return txt

    def result_from_score(score1, score2):
        try:
            s1 = int(score1)
            s2 = int(score2)
        except Exception:
            return ""

        if s1 > s2:
            return "1"
        if s1 < s2:
            return "2"
        return "X"

    def parse_score_text(value):
        txt = str(value or "").strip()

        if txt == "":
            return None, None

        numbers = re.findall(r"\d+", txt)

        if len(numbers) >= 2:
            return int(numbers[0]), int(numbers[1])

        digits = re.sub(r"\D", "", txt)

        if len(digits) == 2:
            return int(digits[0]), int(digits[1])

        return None, None

    def score_to_text(score1, score2):
        if score1 == "" or score2 == "":
            return ""
        return f"{score1}-{score2}"

    def ensure_match_prediction(match_id):
        match_id = str(match_id)

        if match_id not in st.session_state.score_predictions:
            st.session_state.score_predictions[match_id] = {
                "prediction": "",
                "score1": "",
                "score2": "",
            }

    def get_prediction_data(match_id):
        ensure_match_prediction(match_id)
        return st.session_state.score_predictions[str(match_id)]

    def get_score_input_value(match_id):
        data = get_prediction_data(match_id)
        score1 = data.get("score1", "")
        score2 = data.get("score2", "")

        if str(score1).strip() == "" or str(score2).strip() == "":
            return ""

        return f"{score1}-{score2}"

    def update_score_from_input(match_id):
        key = f"score_input_{match_id}"
        raw_value = st.session_state.get(key, "")

        score1, score2 = parse_score_text(raw_value)

        if score1 is None or score2 is None:
            st.session_state.score_predictions[str(match_id)] = {
                "prediction": "",
                "score1": "",
                "score2": "",
            }
            return

        score1 = max(0, min(score1, 50))
        score2 = max(0, min(score2, 50))

        prediction = result_from_score(score1, score2)

        st.session_state.score_predictions[str(match_id)] = {
            "prediction": prediction,
            "score1": score1,
            "score2": score2,
        }

        st.session_state[key] = score_to_text(score1, score2)

    def save_all_predictions():
        saved = batch_save_predictions(
            user_id=user_id,
            local_predictions=st.session_state.score_predictions,
            status="concept",
        )
        st.cache_data.clear()
        return saved

    if "score_predictions" not in st.session_state:
        st.session_state.score_predictions = {}

    loaded_key = f"loaded_score_predictions_{user_id}"

    if loaded_key not in st.session_state:
        st.session_state[loaded_key] = False

    st.markdown("""
    <style>
    .block-container {
        max-width: 820px;
        padding-top: 0 !important;
        padding-left: 0.4rem !important;
        padding-right: 0.4rem !important;
        padding-bottom: 5rem !important;
    }

    section[data-testid="stSidebar"] {
        display: none;
    }

    .st-key-score_top_bar {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        z-index: 999999 !important;
        background: #0e1117 !important;
        padding: 0.28rem 0.45rem 0.35rem 0.45rem !important;
        border-bottom: 1px solid rgba(255,255,255,0.12);
    }

    .st-key-score_top_bar > div {
        max-width: 820px;
        margin-left: auto;
        margin-right: auto;
    }

    .top-spacer {
        height: 66px;
    }

    .st-key-score_save_button button,
    .st-key-score_back_to_main_menu button {
        min-height: 32px !important;
        height: 32px !important;
        border-radius: 10px !important;
        font-size: 0.82rem !important;
        font-weight: 900 !important;
        padding: 0 !important;
    }

    [class*="st-key-score_match_card_"] {
        background: #111827;
        border: 1px solid rgba(255,255,255,0.13);
        border-radius: 14px;
        padding: 0.5rem !important;
        margin-bottom: 0.45rem;
    }

    .match-line {
        font-size: 0.9rem;
        font-weight: 900;
        line-height: 1.2;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .match-meta {
        font-size: 0.76rem;
        color: #cbd5e1;
        line-height: 1.1;
        margin-bottom: 0.18rem;
    }

    .status-dot {
        font-size: 0.8rem;
    }

    .result-badge {
        display: inline-block;
        margin-top: 0.25rem;
        background: rgba(37,99,235,0.20);
        border: 1px solid rgba(96,165,250,0.45);
        border-radius: 999px;
        padding: 0.08rem 0.55rem;
        font-size: 0.78rem;
        font-weight: 900;
        color: #bfdbfe;
    }

    [class*="st-key-score_match_card_"] input {
        height: 38px !important;
        min-height: 38px !important;
        font-size: 1.15rem !important;
        font-weight: 900 !important;
        text-align: center !important;
        border-radius: 12px !important;
    }

    [class*="st-key-score_match_card_"] div[data-testid="stTextInput"] {
        margin-top: 0.35rem !important;
        margin-bottom: 0 !important;
    }

    [class*="st-key-score_match_card_"] label {
        display: none !important;
    }

    footer {
        visibility: hidden;
    }
    </style>
    """, unsafe_allow_html=True)

    @st.cache_data(ttl=60)
    def get_data(active_user_id):
        return load_matches(), load_predictions(active_user_id)

    matches_df, predictions_df = get_data(user_id)

    if not st.session_state[loaded_key]:
        if not predictions_df.empty:
            for _, row in predictions_df.iterrows():
                match_id = str(row.get("match_id", "")).strip()

                if not match_id:
                    continue

                prediction = str(row.get("prediction", "")).upper().strip()
                score1 = row.get("score1", "")
                score2 = row.get("score2", "")

                if prediction in ["1", "X", "2"]:
                    st.session_state.score_predictions[match_id] = {
                        "prediction": prediction,
                        "score1": score1,
                        "score2": score2,
                    }

                    input_key = f"score_input_{match_id}"
                    if input_key not in st.session_state:
                        st.session_state[input_key] = get_score_input_value(match_id)

        st.session_state[loaded_key] = True

    with st.container(key="score_top_bar"):
        col_home, col_save = st.columns([1, 1.4], gap="small")

        with col_home:
            if st.button(
                "☰ Hoofdmenu",
                key="score_back_to_main_menu",
                use_container_width=True,
            ):
                st.session_state.main_page = "🏠 Hoofdmenu"
                st.rerun()

        with col_save:
            if st.button(
                "💾 OPSLAAN",
                key="score_save_button",
                use_container_width=True,
                type="primary",
            ):
                saved = save_all_predictions()
                st.success(f"Opgeslagen: {saved} wedstrijden")

    st.markdown('<div class="top-spacer"></div>', unsafe_allow_html=True)

    wedstrijden = matches_df.copy()

    if wedstrijden.empty:
        st.warning("Geen wedstrijden gevonden.")
        return

    wedstrijden["match_id"] = wedstrijden["match_id"].astype(str).str.strip()

    if "ronde" in wedstrijden.columns:
        wedstrijden = wedstrijden[
            wedstrijden["ronde"]
            .astype(str)
            .str.lower()
            .str.contains("groep", na=False)
        ].copy()

    sort_cols = [c for c in ["datum", "tijd", "match_id"] if c in wedstrijden.columns]

    if sort_cols:
        wedstrijden = wedstrijden.sort_values(sort_cols, kind="stable")

    for _, match in wedstrijden.iterrows():
        match_id = str(match.get("match_id", "")).strip()

        if not match_id:
            continue

        ensure_match_prediction(match_id)

        input_key = f"score_input_{match_id}"

        if input_key not in st.session_state:
            st.session_state[input_key] = get_score_input_value(match_id)

        datum = format_date(match.get("datum", ""))
        tijd = format_time(match.get("tijd", ""))

        team1 = str(match.get("team1", "")).strip()
        team2 = str(match.get("team2", "")).strip()

        team1_code = match.get("team1_code", "")
        team2_code = match.get("team2_code", "")

        data = get_prediction_data(match_id)
        prediction = str(data.get("prediction", "")).upper().strip()
        score1 = str(data.get("score1", "")).strip()
        score2 = str(data.get("score2", "")).strip()

        result_text = ""

        if prediction in ["1", "X", "2"] and score1 != "" and score2 != "":
            result_text = f'<div class="result-badge">{score1}-{score2} → {prediction}</div>'

        with st.container(key=f"score_match_card_{match_id}"):

            st.markdown(
                f"""
<div class="match-meta">
<b>{datum}</b> &nbsp; {tijd} &nbsp; <span class="status-dot">🟢</span>
</div>
<div class="match-line">
{country_flag(team1_code)} {team1}
<span style="color:#9ca3af;">vs</span>
{country_flag(team2_code)} {team2}
</div>
{result_text}
                """,
                unsafe_allow_html=True,
            )

            st.text_input(
                "Uitslag",
                key=input_key,
                placeholder="bv. 21 of 2-1",
                max_chars=5,
                on_change=update_score_from_input,
                args=(match_id,),
            )
