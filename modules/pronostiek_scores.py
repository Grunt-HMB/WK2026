import streamlit as st

from modules.database import (
    load_matches,
    load_predictions,
    batch_save_predictions,
)


def show_pronostiek_scores(user_id="Tom"):

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

    def default_score_for_prediction(prediction):
        prediction = str(prediction or "").upper().strip()

        if prediction == "1":
            return 1, 0

        if prediction == "X":
            return 0, 0

        if prediction == "2":
            return 0, 1

        return 0, 0

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

    def get_score_values(match_id):
        data = get_prediction_data(match_id)

        try:
            score1 = int(float(data.get("score1", 0)))
        except Exception:
            score1 = 0

        try:
            score2 = int(float(data.get("score2", 0)))
        except Exception:
            score2 = 0

        return score1, score2

    def get_prediction(match_id):
        data = get_prediction_data(match_id)
        value = str(data.get("prediction", "")).upper().strip()
        return value if value in ["1", "X", "2"] else None

    def set_score(match_id, score1, score2):
        match_id = str(match_id)

        score1 = max(0, min(int(score1), 50))
        score2 = max(0, min(int(score2), 50))

        prediction = result_from_score(score1, score2)

        st.session_state.score_predictions[match_id] = {
            "prediction": prediction,
            "score1": score1,
            "score2": score2,
        }

        st.session_state[f"score_pred_{match_id}"] = prediction

    def prediction_changed(match_id):
        key = f"score_pred_{match_id}"
        chosen = st.session_state.get(key, None)

        if chosen not in ["1", "X", "2"]:
            return

        data = get_prediction_data(match_id)

        existing_score1 = str(data.get("score1", "")).strip()
        existing_score2 = str(data.get("score2", "")).strip()

        if existing_score1 == "" or existing_score2 == "":
            score1, score2 = default_score_for_prediction(chosen)
        else:
            score1, score2 = get_score_values(match_id)

            current_result = result_from_score(score1, score2)

            if current_result != chosen:
                score1, score2 = default_score_for_prediction(chosen)

        set_score(match_id, score1, score2)

    def save_all_predictions():
        saved = batch_save_predictions(
            user_id=user_id,
            local_predictions=st.session_state.score_predictions,
            status="concept",
        )

        st.cache_data.clear()
        return saved

    # =========================================================
    # SESSION STATE
    # =========================================================

    if "score_predictions" not in st.session_state:
        st.session_state.score_predictions = {}

    loaded_key = f"loaded_score_predictions_{user_id}"

    if loaded_key not in st.session_state:
        st.session_state[loaded_key] = False

    # =========================================================
    # CSS
    # =========================================================

    st.markdown("""
    <style>
    .block-container {
        max-width: 820px;
        padding-top: 0 !important;
        padding-left: 0.35rem !important;
        padding-right: 0.35rem !important;
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
        padding: 0.25rem 0.4rem 0.3rem 0.4rem !important;
        border-bottom: 1px solid rgba(255,255,255,0.12);
    }

    .st-key-score_top_bar > div {
        max-width: 820px;
        margin-left: auto;
        margin-right: auto;
    }

    .top-spacer {
        height: 64px;
    }

    .st-key-score_save_button button,
    .st-key-score_back_to_main_menu button {
        min-height: 31px !important;
        height: 31px !important;
        border-radius: 10px !important;
        font-size: 0.8rem !important;
        font-weight: 900 !important;
        padding: 0 !important;
    }

    [class*="st-key-score_match_card_"] {
        background: #111827;
        border: 1px solid rgba(255,255,255,0.13);
        border-radius: 14px;
        padding: 0.42rem !important;
        margin-bottom: 0.38rem;
        overflow: hidden !important;
    }

    [class*="st-key-score_match_card_"] p {
        margin-bottom: 0 !important;
        line-height: 1.08 !important;
    }

    .match-date-small {
        font-size: 0.72rem;
        color: #cbd5e1;
        line-height: 1.05;
    }

    .match-teams-onecell {
        font-size: 0.86rem;
        font-weight: 900;
        line-height: 1.1;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin-bottom: 0.25rem;
    }

    .score-box {
        height: 27px;
        line-height: 27px;
        width: 28px;
        min-width: 28px;
        max-width: 28px;
        text-align: center;
        font-weight: 900;
        font-size: 0.82rem;
        background: #0b1220;
        border: 1px solid rgba(96,165,250,0.35);
        border-radius: 7px;
    }

    .score-sep {
        height: 27px;
        line-height: 27px;
        width: 8px;
        min-width: 8px;
        max-width: 8px;
        text-align: center;
        font-weight: 900;
        font-size: 0.8rem;
        color: #cbd5e1;
    }

    [class*="st-key-score_match_card_"] div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        gap: 0.08rem !important;
    }

    [class*="st-key-score_match_card_"] div[data-testid="column"] {
        min-width: 0 !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
    }

    [class*="st-key-score_match_card_"] button {
        height: 27px !important;
        min-height: 27px !important;
        padding: 0 !important;
        font-size: 0.76rem !important;
        font-weight: 900 !important;
        border-radius: 7px !important;
    }

    [class*="st-key-score_match_card_"] div[data-testid="stSegmentedControl"] {
        margin: 0 !important;
    }

    [class*="st-key-score_match_card_"] div[data-testid="stSegmentedControl"] button {
        width: 31px !important;
        min-width: 31px !important;
        max-width: 31px !important;
        height: 27px !important;
        min-height: 27px !important;
        padding: 0 !important;
        font-size: 0.74rem !important;
    }

    [class*="st-key-score_match_card_"] div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(1) {
        flex: 0 0 96px !important;
        width: 96px !important;
        max-width: 96px !important;
    }

    [class*="st-key-score_match_card_"] div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2),
    [class*="st-key-score_match_card_"] div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(4),
    [class*="st-key-score_match_card_"] div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(6),
    [class*="st-key-score_match_card_"] div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(8) {
        flex: 0 0 29px !important;
        width: 29px !important;
        max-width: 29px !important;
    }

    [class*="st-key-score_match_card_"] div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(3),
    [class*="st-key-score_match_card_"] div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(7) {
        flex: 0 0 30px !important;
        width: 30px !important;
        max-width: 30px !important;
    }

    [class*="st-key-score_match_card_"] div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(5) {
        flex: 0 0 9px !important;
        width: 9px !important;
        max-width: 9px !important;
    }

    footer {
        visibility: hidden;
    }
    </style>
    """, unsafe_allow_html=True)

    # =========================================================
    # DATA
    # =========================================================

    @st.cache_data(ttl=60)
    def get_data(active_user_id):
        return load_matches(), load_predictions(active_user_id)

    matches_df, predictions_df = get_data(user_id)

    # =========================================================
    # LOAD SAVED PREDICTIONS
    # =========================================================

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

        st.session_state[loaded_key] = True

    # =========================================================
    # TOP BAR
    # =========================================================

    with st.container(key="score_top_bar"):
        col_home, col_save = st.columns([1, 1.25], gap="small")

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

    # =========================================================
    # WEDSTRIJDEN
    # =========================================================

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

        datum = format_date(match.get("datum", ""))
        tijd = format_time(match.get("tijd", ""))

        team1 = str(match.get("team1", "")).strip()
        team2 = str(match.get("team2", "")).strip()

        team1_code = match.get("team1_code", "")
        team2_code = match.get("team2_code", "")

        pred_key = f"score_pred_{match_id}"

        if pred_key not in st.session_state:
            st.session_state[pred_key] = get_prediction(match_id)

        score1, score2 = get_score_values(match_id)

        with st.container(key=f"score_match_card_{match_id}"):

            st.markdown(
                f"""
<div class="match-date-small">
<b>{datum}</b> &nbsp; {tijd} &nbsp; 🟢
</div>
<div class="match-teams-onecell">
{country_flag(team1_code)} {team1}
<span style="color:#9ca3af;">vs</span>
{country_flag(team2_code)} {team2}
</div>
                """,
                unsafe_allow_html=True,
            )

            c_pred, c_m1, c_s1, c_p1, c_sep, c_m2, c_s2, c_p2 = st.columns(
                [96, 29, 30, 29, 9, 29, 30, 29],
                gap="small",
            )

            with c_pred:
                st.segmented_control(
                    "Pronostiek",
                    ["1", "X", "2"],
                    key=pred_key,
                    label_visibility="collapsed",
                    on_change=prediction_changed,
                    args=(match_id,),
                )

            with c_m1:
                if st.button("−", key=f"minus1_{match_id}", use_container_width=True):
                    set_score(match_id, max(score1 - 1, 0), score2)
                    st.rerun()

            with c_s1:
                st.markdown(
                    f'<div class="score-box">{score1}</div>',
                    unsafe_allow_html=True,
                )

            with c_p1:
                if st.button("+", key=f"plus1_{match_id}", use_container_width=True):
                    set_score(match_id, score1 + 1, score2)
                    st.rerun()

            with c_sep:
                st.markdown(
                    '<div class="score-sep">-</div>',
                    unsafe_allow_html=True,
                )

            with c_m2:
                if st.button("−", key=f"minus2_{match_id}", use_container_width=True):
                    set_score(match_id, score1, max(score2 - 1, 0))
                    st.rerun()

            with c_s2:
                st.markdown(
                    f'<div class="score-box">{score2}</div>',
                    unsafe_allow_html=True,
                )

            with c_p2:
                if st.button("+", key=f"plus2_{match_id}", use_container_width=True):
                    set_score(match_id, score1, score2 + 1)
                    st.rerun()
