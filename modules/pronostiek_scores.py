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
            s1, s2 = int(score1), int(score2)
        except:
            return ""
        if s1 > s2: return "1"
        if s1 < s2: return "2"
        return "X"

    def default_score_for_prediction(prediction):
        prediction = str(prediction or "").upper().strip()
        if prediction == "1": return 1, 0
        if prediction == "X": return 0, 0
        if prediction == "2": return 0, 1
        return 0, 0

    def ensure_match_prediction(match_id):
        match_id = str(match_id)
        if match_id not in st.session_state.score_predictions:
            st.session_state.score_predictions[match_id] = {
                "prediction": "", "score1": "", "score2": "",
            }

    def get_prediction_data(match_id):
        ensure_match_prediction(match_id)
        return st.session_state.score_predictions[str(match_id)]

    def get_score_values(match_id):
        data = get_prediction_data(match_id)
        try:
            s1 = int(float(data.get("score1", 0)))
            s2 = int(float(data.get("score2", 0)))
        except:
            s1, s2 = 0, 0
        return s1, s2

    def set_score(match_id, score1, score2):
        match_id = str(match_id)
        score1, score2 = max(0, min(int(score1), 50)), max(0, min(int(score2), 50))
        prediction = result_from_score(score1, score2)
        st.session_state.score_predictions[match_id] = {
            "prediction": prediction, "score1": score1, "score2": score2,
        }
        st.session_state[f"score_pred_{match_id}"] = prediction

    def prediction_changed(match_id):
        key = f"score_pred_{match_id}"
        chosen = st.session_state.get(key)
        if chosen not in ["1", "X", "2"]: return
        
        data = get_prediction_data(match_id)
        s1_existing = str(data.get("score1", "")).strip()
        s2_existing = str(data.get("score2", "")).strip()

        if s1_existing == "" or s2_existing == "":
            s1, s2 = default_score_for_prediction(chosen)
        else:
            s1, s2 = get_score_values(match_id)
            if result_from_score(s1, s2) != chosen:
                s1, s2 = default_score_for_prediction(chosen)
        set_score(match_id, s1, s2)

    def save_all_predictions():
        saved = batch_save_predictions(
            user_id=user_id,
            local_predictions=st.session_state.score_predictions,
            status="concept",
        )
        st.cache_data.clear()
        return saved

    # --- Session State Init ---
    if "score_predictions" not in st.session_state:
        st.session_state.score_predictions = {}
    
    loaded_key = f"loaded_score_predictions_{user_id}"
    if loaded_key not in st.session_state:
        st.session_state[loaded_key] = False

    # --- CSS VOOR MOBIEL ---
    st.markdown("""
    <style>
    .block-container { max-width: 820px; padding-top: 0 !important; padding-left: 0.35rem !important; padding-right: 0.35rem !important; }
    section[data-testid="stSidebar"] { display: none; }

    /* Fix voor mobiele kolommen: voorkom dat ze stapelen of te breed worden */
    [data-testid="column"] {
        min-width: 0 !important;
        flex: 1 1 auto !important;
    }
    
    [data-testid="stHorizontalBlock"] {
        gap: 0.15rem !important;
        align-items: center !important;
    }

    .st-key-score_top_bar {
        position: fixed !important; top: 0; left: 0; right: 0; z-index: 999999;
        background: #0e1117; padding: 0.25rem 0.4rem; border-bottom: 1px solid rgba(255,255,255,0.12);
    }
    .top-spacer { height: 60px; }

    /* Kaart styling */
    [class*="st-key-score_match_card_"] {
        background: #111827; border: 1px solid rgba(255,255,255,0.13);
        border-radius: 12px; padding: 0.5rem !important; margin-bottom: 0.4rem;
    }

    .match-teams-onecell { font-size: 0.85rem; font-weight: 800; margin-bottom: 0.4rem; }
    
    /* Score display box */
    .score-display {
        width: 100%; height: 28px; line-height: 28px; text-align: center;
        font-weight: 900; background: #0b1220; border: 1px solid rgba(255,255,255,0.2);
        border-radius: 6px; font-size: 0.9rem;
    }
    .score-sep { text-align: center; font-weight: 900; color: #94a3b8; }

    /* Button styling binnen de kaart */
    [class*="st-key-score_match_card_"] button {
        height: 28px !important; min-height: 28px !important;
        padding: 0 !important; border-radius: 6px !important; line-height: 1 !important;
    }
    
    /* Segmented control compacter */
    div[data-testid="stSegmentedControl"] button {
        height: 28px !important; min-width: 32px !important; font-size: 0.75rem !important;
    }

    footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

    # --- Data Laden ---
    @st.cache_data(ttl=60)
    def get_data(active_user_id):
        return load_matches(), load_predictions(active_user_id)

    matches_df, predictions_df = get_data(user_id)

    if not st.session_state[loaded_key]:
        if not predictions_df.empty:
            for _, row in predictions_df.iterrows():
                m_id = str(row.get("match_id", "")).strip()
                if m_id:
                    st.session_state.score_predictions[m_id] = {
                        "prediction": str(row.get("prediction", "")).upper().strip(),
                        "score1": row.get("score1", ""),
                        "score2": row.get("score2", ""),
                    }
        st.session_state[loaded_key] = True

    # --- Top Bar ---
    with st.container(key="score_top_bar"):
        c1, c2 = st.columns([1, 1])
        with c1:
            if st.button("☰ Menu", key="score_back_to_main_menu", use_container_width=True):
                st.session_state.main_page = "🏠 Hoofdmenu"
                st.rerun()
        with c2:
            if st.button("💾 OPSLAAN", key="score_save_button", use_container_width=True, type="primary"):
                saved = save_all_predictions()
                st.toast(f"✅ Opgeslagen: {saved} wedstrijden")

    st.markdown('<div class="top-spacer"></div>', unsafe_allow_html=True)

    # --- Match Lijst ---
    wedstrijden = matches_df.copy()
    if wedstrijden.empty:
        st.warning("Geen wedstrijden gevonden.")
        return

    wedstrijden["match_id"] = wedstrijden["match_id"].astype(str).str.strip()
    if "ronde" in wedstrijden.columns:
        wedstrijden = wedstrijden[wedstrijden["ronde"].astype(str).str.lower().str.contains("groep", na=False)].copy()

    sort_cols = [c for c in ["datum", "tijd", "match_id"] if c in wedstrijden.columns]
    if sort_cols:
        wedstrijden = wedstrijden.sort_values(sort_cols, kind="stable")

    for _, match in wedstrijden.iterrows():
        m_id = match["match_id"]
        ensure_match_prediction(m_id)
        
        team1, team2 = str(match.get("team1", "")), str(match.get("team2", ""))
        t1_c, t2_c = match.get("team1_code", ""), match.get("team2_code", "")
        
        pred_key = f"score_pred_{m_id}"
        if pred_key not in st.session_state:
            st.session_state[pred_key] = get_prediction_data(m_id).get("prediction")

        s1, s2 = get_score_values(m_id)

        with st.container(key=f"score_match_card_{m_id}"):
            st.markdown(f"""
                <div class="match-teams-onecell">
                    {country_flag(t1_c)} {team1} <span style="color:#64748b;">vs</span> {country_flag(t2_c)} {team2}
                </div>""", unsafe_allow_html=True)

            # Aangepaste kolom-verhouding voor mobiel:
            # 1/X/2 krijgt wat meer ruimte, de score-knoppen staan strak naast elkaar
            col_p, col_m1, col_s1, col_p1, col_x, col_m2, col_s2, col_p2 = st.columns(
                [2.2, 0.6, 0.6, 0.6, 0.2, 0.6, 0.6, 0.6]
            )

            with col_p:
                st.segmented_control("P", ["1", "X", "2"], key=pred_key, 
                                     label_visibility="collapsed", on_change=prediction_changed, args=(m_id,))
            
            with col_m1:
                if st.button("−", key=f"m1_{m_id}", use_container_width=True):
                    set_score(m_id, max(s1 - 1, 0), s2); st.rerun()
            with col_s1:
                st.markdown(f'<div class="score-display">{s1}</div>', unsafe_allow_html=True)
            with col_p1:
                if st.button("+", key=f"p1_{m_id}", use_container_width=True):
                    set_score(m_id, s1 + 1, s2); st.rerun()

            with col_x:
                st.markdown('<div class="score-sep">-</div>', unsafe_allow_html=True)

            with col_m2:
                if st.button("−", key=f"m2_{m_id}", use_container_width=True):
                    set_score(m_id, s1, max(s2 - 1, 0)); st.rerun()
            with col_s2:
                st.markdown(f'<div class="score-display">{s2}</div>', unsafe_allow_html=True)
            with col_p2:
                if st.button("+", key=f"p2_{m_id}", use_container_width=True):
                    set_score(m_id, s1, s2 + 1); st.rerun()
