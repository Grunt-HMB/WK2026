import streamlit as st
import pandas as pd
from modules.database import (
    load_matches,
    load_predictions,
    batch_save_predictions,
)

def show_pronostiek_scores(user_id="Tom", standings_df=None):
    # ==================== HELPERS ====================
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

    # ==================== SESSION STATE ====================
    if "local_predictions" not in st.session_state:
        st.session_state.local_predictions = {}

    loaded_key = f"loaded_predictions_{user_id}"
    if loaded_key not in st.session_state:
        st.session_state[loaded_key] = False

    # ==================== CSS ====================
    st.markdown("""
    <style>
    .block-container { padding-bottom: 5rem !important; }
    [class*="st-key-match_card_"] {
        background: #111827;
        border: 1px solid rgba(255,255,255,0.13);
        border-radius: 14px;
        padding: 0.6rem !important;
        margin-bottom: 0.6rem;
    }
    .score-inputs {
        margin-top: 8px;
    }
    .score-label {
        font-size: 0.75rem;
        color: #94a3b8;
        margin-bottom: 2px;
    }
    </style>
    """, unsafe_allow_html=True)

    # ==================== DATA ====================
    @st.cache_data(ttl=60)
    def get_data(active_user_id):
        return load_matches(), load_predictions(active_user_id)

    matches_df, predictions_df = get_data(user_id)

    # Load saved predictions
    if not st.session_state[loaded_key]:
        if not predictions_df.empty:
            for _, row in predictions_df.iterrows():
                mid = str(row.get("match_id", "")).strip()
                if mid and str(row.get("prediction", "")).upper() in ["1", "X", "2"]:
                    st.session_state.local_predictions[mid] = {
                        "prediction": str(row.get("prediction", "")).upper(),
                        "score1": row.get("score1", 0),
                        "score2": row.get("score2", 0),
                    }
        st.session_state[loaded_key] = True

    # ==================== TOP BAR ====================
    with st.container(key="top_bar"):
        col_home, col_save = st.columns([1, 1.4], gap="small")
        with col_home:
            if st.button("☰ Hoofdmenu", key="back_to_main_menu", use_container_width=True):
                st.session_state.main_page = "🏠 Hoofdmenu"
                st.rerun()
        with col_save:
            if st.button("💾 OPSLAAN", key="save_button", use_container_width=True, type="primary"):
                saved = batch_save_predictions(
                    user_id=user_id,
                    local_predictions=st.session_state.local_predictions,
                    status="concept",
                )
                st.success(f"Opgeslagen: {saved} wedstrijden")

    st.markdown('<div class="top-spacer"></div>', unsafe_allow_html=True)

    # ==================== MATCHES ====================
    wedstrijden = matches_df.copy()
    if wedstrijden.empty:
        st.warning("Geen wedstrijden gevonden.")
        return

    wedstrijden["match_id"] = wedstrijden["match_id"].astype(str).str.strip()
    # Optional: filter group stage only
    if "ronde" in wedstrijden.columns:
        wedstrijden = wedstrijden[wedstrijden["ronde"].astype(str).str.lower().str.contains("groep", na=False)].copy()

    for _, match in wedstrijden.iterrows():
        match_id = str(match.get("match_id", "")).strip()
        if not match_id:
            continue

        datum = format_date(match.get("datum", ""))
        tijd = format_time(match.get("tijd", ""))
        team1 = str(match.get("team1", "")).strip()
        team2 = str(match.get("team2", "")).strip()
        team1_code = match.get("team1_code", "")
        team2_code = match.get("team2_code", "")

        pred_key = f"pred_{match_id}"

        # Get current prediction
        current_pred = st.session_state.local_predictions.get(match_id, {}).get("prediction")

        with st.container(key=f"match_card_{match_id}"):
            col_info, col_pred = st.columns([2.1, 1], gap="small")

            with col_info:
                st.markdown(f"""
                <div class="match-date-small">
                    <b>{datum}</b> &nbsp; {tijd} &nbsp; 🟢
                </div>
                <div class="match-teams-onecell">
                    {country_flag(team1_code)} {team1}
                    <span style="color:#9ca3af;">vs</span>
                    {country_flag(team2_code)} {team2}
                </div>
                """, unsafe_allow_html=True)

            with col_pred:
                # 1 / X / 2 selector
                selected = st.segmented_control(
                    label="Pronostiek",
                    options=["1", "X", "2"],
                    key=pred_key,
                    default=current_pred,
                    label_visibility="collapsed",
                )

                # Update local predictions
                if selected:
                    if match_id not in st.session_state.local_predictions:
                        st.session_state.local_predictions[match_id] = {}
                    st.session_state.local_predictions[match_id]["prediction"] = selected

                # ==================== SCORE INPUTS (appear after selection) ====================
                if selected:
                    st.markdown('<div class="score-inputs">', unsafe_allow_html=True)
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown("<div class='score-label'>Score " + team1 + "</div>", unsafe_allow_html=True)
                        score1 = st.number_input(
                            label="",
                            min_value=0,
                            max_value=15,
                            value=int(st.session_state.local_predictions[match_id].get("score1", 0)),
                            key=f"score1_{match_id}",
                            label_visibility="collapsed"
                        )
                        st.session_state.local_predictions[match_id]["score1"] = score1

                    with c2:
                        st.markdown("<div class='score-label'>Score " + team2 + "</div>", unsafe_allow_html=True)
                        score2 = st.number_input(
                            label="",
                            min_value=0,
                            max_value=15,
                            value=int(st.session_state.local_predictions[match_id].get("score2", 0)),
                            key=f"score2_{match_id}",
                            label_visibility="collapsed"
                        )
                        st.session_state.local_predictions[match_id]["score2"] = score2

                    st.markdown('</div>', unsafe_allow_html=True)
