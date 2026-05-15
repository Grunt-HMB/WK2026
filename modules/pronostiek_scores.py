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

        return (
            chr(ord(code[0]) + 127397)
            + chr(ord(code[1]) + 127397)
        )

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

    def ensure_match_prediction(match_id):

        match_id = str(match_id)

        if match_id not in st.session_state.score_predictions:

            st.session_state.score_predictions[match_id] = {
                "prediction": "",
                "score1": 0,
                "score2": 0,
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
        padding: 0.3rem 0.45rem 0.35rem 0.45rem !important;
        border-bottom: 1px solid rgba(255,255,255,0.12);
    }

    .st-key-score_top_bar > div {
        max-width: 820px;
        margin-left: auto;
        margin-right: auto;
    }

    .top-spacer {
        height: 68px;
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

        overflow: hidden !important;
    }

    .match-meta {

        font-size: 0.74rem;

        color: #cbd5e1;

        line-height: 1.05;

        margin-bottom: 0.14rem;
    }

    .match-line {

        font-size: 0.9rem;

        font-weight: 900;

        line-height: 1.12;

        white-space: nowrap;

        overflow: hidden;

        text-overflow: ellipsis;

        margin-bottom: 0.35rem;
    }

    .result-badge {

        display: inline-block;

        margin-left: 0.3rem;

        background: rgba(37,99,235,0.20);

        border: 1px solid rgba(96,165,250,0.55);

        border-radius: 999px;

        padding: 0.02rem 0.45rem;

        font-size: 0.76rem;

        font-weight: 900;

        color: #bfdbfe;

        vertical-align: middle;
    }

    .score-value {

        width: 32px;

        min-width: 32px;

        max-width: 32px;

        height: 32px;

        line-height: 32px;

        text-align: center;

        font-weight: 900;

        font-size: 1rem;

        background: #0b1220;

        border: 1px solid rgba(255,255,255,0.18);

        border-radius: 8px;

        margin-left: auto;

        margin-right: auto;
    }

    .score-gap {

        width: 10px;

        min-width: 10px;

        max-width: 10px;

        height: 32px;

        line-height: 32px;

        text-align: center;

        color: #64748b;

        font-weight: 900;
    }

    [class*="st-key-score_match_card_"] div[data-testid="stHorizontalBlock"] {

        display: flex !important;

        flex-direction: row !important;

        flex-wrap: nowrap !important;

        gap: 0.12rem !important;

        align-items: center !important;
    }

    [class*="st-key-score_match_card_"] div[data-testid="column"] {

        min-width: 0 !important;

        padding-left: 0 !important;

        padding-right: 0 !important;
    }

    [class*="st-key-score_match_card_"] button {

        width: 32px !important;

        min-width: 32px !important;

        max-width: 32px !important;

        height: 32px !important;

        min-height: 32px !important;

        padding: 0 !important;

        font-weight: 900 !important;

        font-size: 1rem !important;

        border-radius: 8px !important;
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

        return (
            load_matches(),
            load_predictions(active_user_id),
        )

    matches_df, predictions_df = get_data(user_id)

    # =========================================================
    # LOAD SAVED PREDICTIONS
    # =========================================================

    if not st.session_state[loaded_key]:

        if not predictions_df.empty:

            for _, row in predictions_df.iterrows():

                match_id = str(
                    row.get("match_id", "")
                ).strip()

                if not match_id:
                    continue

                prediction = str(
                    row.get("prediction", "")
                ).upper().strip()

                score1 = row.get("score1", 0)
                score2 = row.get("score2", 0)

                try:
                    score1 = int(float(score1))

                except Exception:
                    score1 = 0

                try:
                    score2 = int(float(score2))

                except Exception:
                    score2 = 0

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

        col_home, col_save = st.columns(
            [1, 1.4],
            gap="small",
        )

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

                st.success(
                    f"Opgeslagen: {saved} wedstrijden"
                )

    st.markdown(
        '<div class="top-spacer"></div>',
        unsafe_allow_html=True,
    )

    # =========================================================
    # WEDSTRIJDEN
    # =========================================================

    wedstrijden = matches_df.copy()

    if wedstrijden.empty:

        st.warning("Geen wedstrijden gevonden.")

        return

    wedstrijden["match_id"] = (
        wedstrijden["match_id"]
        .astype(str)
        .str.strip()
    )

    if "ronde" in wedstrijden.columns:

        wedstrijden = wedstrijden[
            wedstrijden["ronde"]
            .astype(str)
            .str.lower()
            .str.contains("groep", na=False)
        ].copy()

    sort_cols = [
        c for c in ["datum", "tijd", "match_id"]
        if c in wedstrijden.columns
    ]

    if sort_cols:

        wedstrijden = wedstrijden.sort_values(
            sort_cols,
            kind="stable",
        )

    for _, match in wedstrijden.iterrows():

        match_id = str(
            match.get("match_id", "")
        ).strip()

        if not match_id:
            continue

        ensure_match_prediction(match_id)

        datum = format_date(
            match.get("datum", "")
        )

        tijd = format_time(
            match.get("tijd", "")
        )

        team1 = str(
            match.get("team1", "")
        ).strip()

        team2 = str(
            match.get("team2", "")
        ).strip()

        team1_code = match.get(
            "team1_code",
            "",
        )

        team2_code = match.get(
            "team2_code",
            "",
        )

        score1, score2 = get_score_values(match_id)

        prediction = result_from_score(
            score1,
            score2,
        )

        with st.container(
            key=f"score_match_card_{match_id}"
        ):

            st.markdown(
                f"""
<div class="match-meta">
<b>{datum}</b> &nbsp; {tijd} &nbsp; 🟢
</div>

<div class="match-line">
{country_flag(team1_code)} {team1}
<span style="color:#9ca3af;">vs</span>
{country_flag(team2_code)} {team2}

<span class="result-badge">
{prediction}
</span>
</div>
                """,
                unsafe_allow_html=True,
            )

            c_m1, c_v1, c_p1, c_gap, c_m2, c_v2, c_p2 = st.columns(
                [1, 1, 1, 0.25, 1, 1, 1],
                gap="small",
            )

            with c_m1:

                if st.button(
                    "−",
                    key=f"minus1_{match_id}",
                ):

                    set_score(
                        match_id,
                        max(score1 - 1, 0),
                        score2,
                    )

                    st.rerun()

            with c_v1:

                st.markdown(
                    f"""
<div class="score-value">
{score1}
</div>
                    """,
                    unsafe_allow_html=True,
                )

            with c_p1:

                if st.button(
                    "+",
                    key=f"plus1_{match_id}",
                ):

                    set_score(
                        match_id,
                        score1 + 1,
                        score2,
                    )

                    st.rerun()

            with c_gap:

                st.markdown(
                    """
<div class="score-gap">
-
</div>
                    """,
                    unsafe_allow_html=True,
                )

            with c_m2:

                if st.button(
                    "−",
                    key=f"minus2_{match_id}",
                ):

                    set_score(
                        match_id,
                        score1,
                        max(score2 - 1, 0),
                    )

                    st.rerun()

            with c_v2:

                st.markdown(
                    f"""
<div class="score-value">
{score2}
</div>
                    """,
                    unsafe_allow_html=True,
                )

            with c_p2:

                if st.button(
                    "+",
                    key=f"plus2_{match_id}",
                ):

                    set_score(
                        match_id,
                        score1,
                        score2 + 1,
                    )

                    st.rerun()
