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
            if s1 > s2: return "1"
            if s1 < s2: return "2"
            return "X"
        except Exception:
            return ""

    def ensure_match_prediction(match_id):
        match_id = str(match_id)
        if "score_predictions" not in st.session_state:
            st.session_state.score_predictions = {}
        if match_id not in st.session_state.score_predictions:
            st.session_state.score_predictions[match_id] = {
                "prediction": "",
                "score1": 0,
                "score2": 0,
            }

    # =========================================================
    # CALLBACKS (Voorkomen de volledige rerun-vertraging)
    # =========================================================

    def update_score_callback(match_id, team_num, delta):
        """Update de score in session_state zonder handmatige st.rerun()"""
        match_id = str(match_id)
        ensure_match_prediction(match_id)
        
        current_data = st.session_state.score_predictions[match_id]
        field = f"score{team_num}"
        
        # Bereken nieuwe waarde (min 0, max 50)
        old_val = current_data.get(field, 0)
        new_val = max(0, min(int(old_val) + delta, 50))
        
        current_data[field] = new_val
        # Update ook direct de 1-X-2 voorspelling
        current_data["prediction"] = result_from_score(
            current_data["score1"], 
            current_data["score2"]
        )

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
    # CSS (Verbeterd voor de +/- buttons)
    # =========================================================

    st.markdown("""
    <style>
    .block-container {
        max-width: 820px;
        padding-top: 0 !important;
        padding-left: 0.4rem !important;
        padding-right: 0.4rem !important;
        padding-bottom: 5rem !important;
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

    .top-spacer { height: 66px; }

    [class*="st-key-score_match_card_"] {
        background: #111827;
        border: 1px solid rgba(255,255,255,0.13);
        border-radius: 14px;
        padding: 0.8rem !important;
        margin-bottom: 0.45rem;
    }

    .match-meta { font-size: 0.75rem; color: #cbd5e1; margin-bottom: 0.12rem; }
    .match-line { font-size: 0.95rem; font-weight: 900; margin-bottom: 0.5rem; }
    
    .result-badge {
        display: inline-block;
        margin-left: 0.5rem;
        background: rgba(37,99,235,0.25);
        border: 1px solid #60a5fa;
        border-radius: 8px;
        padding: 0.1rem 0.5rem;
        font-size: 0.8rem;
        color: #bfdbfe;
    }

    .score-value {
        height: 36px;
        line-height: 36px;
        text-align: center;
        font-weight: 900;
        font-size: 1.1rem;
        background: #0b1220;
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 9px;
    }

    .score-gap { line-height: 36px; text-align: center; color: #64748b; font-weight: 900; }
    
    footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

    # =========================================================
    # DATA
    # =========================================================

    @st.cache_data(ttl=60)
    def get_data(active_user_id):
        return load_matches(), load_predictions(active_user_id)

    matches_df, predictions_df = get_data(user_id)

    # Inladen van database naar session_state (eenmalig)
    if not st.session_state[loaded_key]:
        if not predictions_df.empty:
            for _, row in predictions_df.iterrows():
                m_id = str(row.get("match_id", "")).strip()
                if not m_id: continue
                
                try:
                    s1 = int(float(row.get("score1", 0)))
                    s2 = int(float(row.get("score2", 0)))
                except:
                    s1, s2 = 0, 0

                st.session_state.score_predictions[m_id] = {
                    "prediction": result_from_score(s1, s2),
                    "score1": s1,
                    "score2": s2,
                }
        st.session_state[loaded_key] = True

    # =========================================================
    # TOP BAR
    # =========================================================

    with st.container(key="score_top_bar"):
        col_home, col_save = st.columns([1, 1.4], gap="small")
        with col_home:
            if st.button("☰ Menu", key="btn_home", use_container_width=True):
                st.session_state.main_page = "🏠 Hoofdmenu"
                st.rerun()
        with col_save:
            if st.button("💾 OPSLAAN", key="btn_save", type="primary", use_container_width=True):
                saved = save_all_predictions()
                st.success(f"Opgeslagen: {saved} wedstrijden")

    st.markdown('<div class="top-spacer"></div>', unsafe_allow_html=True)

    # =========================================================
    # WEDSTRIJDEN LIJST
    # =========================================================

    wedstrijden = matches_df.copy()
    if wedstrijden.empty:
        st.warning("Geen wedstrijden gevonden.")
        return

    # Filter op ronde
    if "ronde" in wedstrijden.columns:
        wedstrijden = wedstrijden[wedstrijden["ronde"].astype(str).str.lower().str.contains("groep", na=False)].copy()

    # Sorteren
    sort_cols = [c for c in ["datum", "tijd", "match_id"] if c in wedstrijden.columns]
    if sort_cols:
        wedstrijden = wedstrijden.sort_values(sort_cols, kind="stable")

    for _, match in wedstrijden.iterrows():
        m_id = str(match.get("match_id", "")).strip()
        if not m_id: continue

        ensure_match_prediction(m_id)
        
        # Haal huidige waarden uit session_state
        data = st.session_state.score_predictions[m_id]
        score1 = data["score1"]
        score2 = data["score2"]
        prediction = data["prediction"]

        with st.container(key=f"score_match_card_{m_id}"):
            # Match Info
            st.markdown(f"""
                <div class="match-meta"><b>{format_date(match.get('datum'))}</b> &nbsp; {format_time(match.get('tijd'))}</div>
                <div class="match-line">
                    {country_flag(match.get('team1_code'))} {match.get('team1')} 
                    <span style="color:#9ca3af;">vs</span> 
                    {match.get('team2')} {country_flag(match.get('team2_code'))}
                    <span class="result-badge">{prediction}</span>
                </div>
            """, unsafe_allow_html=True)

            # Controls (Zonder st.rerun, maar met on_click callbacks)
            c_m1, c_v1, c_p1, c_gap, c_m2, c_v2, c_p2 = st.columns([1, 1, 1, 0.35, 1, 1, 1], gap="small")

            with c_m1:
                st.button("−", key=f"m1_{m_id}", on_click=update_score_callback, args=(m_id, 1, -1), use_container_width=True)
            with c_v1:
                st.markdown(f"<div class='score-value'>{score1}</div>", unsafe_allow_html=True)
            with c_p1:
                st.button("+", key=f"p1_{m_id}", on_click=update_score_callback, args=(m_id, 1, 1), use_container_width=True)

            with c_gap:
                st.markdown("<div class='score-gap'>-</div>", unsafe_allow_html=True)

            with c_m2:
                st.button("−", key=f"m2_{m_id}", on_click=update_score_callback, args=(m_id, 2, -1), use_container_width=True)
            with v2:
                st.markdown(f"<div class='score-value'>{score2}</div>", unsafe_allow_html=True)
            with c_p2:
                st.button("+", key=f"p2_{m_id}", on_click=update_score_callback, args=(m_id, 2, 1), use_container_width=True)
