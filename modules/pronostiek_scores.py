import streamlit as st
import pandas as pd

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

    def get_prediction_data(match_id):
        return st.session_state.score_predictions.get(
            str(match_id),
            {
                "prediction": "",
                "score1": "",
                "score2": "",
            },
        )

    def get_prediction(match_id):
        data = get_prediction_data(match_id)

        if isinstance(data, dict):
            value = data.get("prediction", "")
        else:
            value = data

        value = str(value).upper().strip()

        return value if value in ["1", "X", "2"] else None

    def get_score_text(match_id):
        data = get_prediction_data(match_id)

        if not isinstance(data, dict):
            return ""

        score1 = str(data.get("score1", "")).strip()
        score2 = str(data.get("score2", "")).strip()

        if score1 == "" or score2 == "":
            return ""

        return f"{score1} - {score2}"

    def prediction_clicked(match_id):
        key = f"score_pred_{match_id}"
        chosen = st.session_state.get(key, None)

        if chosen not in ["1", "X", "2"]:
            return

        st.session_state.pending_score_match_id = str(match_id)
        st.session_state.pending_score_choice = chosen

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

    if "pending_score_match_id" not in st.session_state:
        st.session_state.pending_score_match_id = ""

    if "pending_score_choice" not in st.session_state:
        st.session_state.pending_score_choice = ""

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
        padding-left: 0.45rem !important;
        padding-right: 0.45rem !important;
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
        padding: 0.35rem 0.5rem 0.45rem 0.5rem !important;
        border-bottom: 1px solid rgba(255,255,255,0.12);
    }

    .st-key-score_top_bar > div {
        max-width: 820px;
        margin-left: auto;
        margin-right: auto;
    }

    .top-spacer {
        height: 78px;
    }

    .st-key-score_save_button button {
        min-height: 34px !important;
        height: 34px !important;
        border-radius: 10px !important;
        font-size: 0.82rem !important;
        font-weight: 900 !important;
    }

    [class*="st-key-score_match_card_"] {
        background: #111827;
        border: 1px solid rgba(255,255,255,0.13);
        border-radius: 14px;
        padding: 0.55rem !important;
        margin-bottom: 0.5rem;
    }

    [class*="st-key-score_match_card_"] p {
        margin-bottom: 0 !important;
        line-height: 1.22 !important;
    }

    .match-date-small {
        font-size: 0.78rem;
        color: #cbd5e1;
        line-height: 1.15;
    }

    .match-teams-onecell {
        font-size: 0.92rem;
        font-weight: 800;
        line-height: 1.22;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .score-pill {
        display: inline-block;
        margin-top: 0.25rem;
        background: rgba(37,99,235,0.25);
        border: 1px solid rgba(96,165,250,0.45);
        border-radius: 999px;
        padding: 0.1rem 0.55rem;
        font-size: 0.78rem;
        font-weight: 900;
        color: #bfdbfe;
    }

    [class*="st-key-score_match_card_"] div[data-testid="stSegmentedControl"] {
        margin-top: 0.35rem !important;
    }

    [class*="st-key-score_match_card_"] div[data-testid="stSegmentedControl"] button {
        min-width: 46px !important;
        height: 31px !important;
        padding: 0 !important;
        font-weight: 800 !important;
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
    # DIALOG
    # =========================================================

    @st.dialog("🎯 Score invullen")
    def score_dialog(match):
        match_id = str(match.get("match_id", "")).strip()

        team1 = str(match.get("team1", "")).strip()
        team2 = str(match.get("team2", "")).strip()

        chosen = str(st.session_state.get("pending_score_choice", "")).upper().strip()

        existing = get_prediction_data(match_id)

        existing_score1 = existing.get("score1", "") if isinstance(existing, dict) else ""
        existing_score2 = existing.get("score2", "") if isinstance(existing, dict) else ""

        score1_key = f"dialog_score1_value_{match_id}"
        score2_key = f"dialog_score2_value_{match_id}"

        if score1_key not in st.session_state or score2_key not in st.session_state:
            if str(existing_score1).strip() != "" and str(existing_score2).strip() != "":
                st.session_state[score1_key] = int(float(existing_score1))
                st.session_state[score2_key] = int(float(existing_score2))
            else:
                default_score1, default_score2 = default_score_for_prediction(chosen)
                st.session_state[score1_key] = default_score1
                st.session_state[score2_key] = default_score2

        def keypad(score_key, title):
            st.markdown(f"#### {title}")

            st.markdown(
                f"""
<div style="
    text-align:center;
    font-size:2rem;
    font-weight:900;
    background:#111827;
    border:1px solid rgba(255,255,255,0.18);
    border-radius:14px;
    padding:0.35rem;
    margin-bottom:0.45rem;
">
{st.session_state[score_key]}
</div>
                """,
                unsafe_allow_html=True,
            )

            rows = [
                ["1", "2", "3"],
                ["4", "5", "6"],
                ["7", "8", "9"],
                ["C", "0", "←"],
                ["-", "+", ""],
            ]

            for r, row in enumerate(rows):
                cols = st.columns(3, gap="small")

                for c, label in enumerate(row):
                    with cols[c]:
                        if label == "":
                            st.write("")
                            continue

                        if st.button(
                            label,
                            key=f"keypad_{score_key}_{r}_{c}_{label}",
                            use_container_width=True,
                        ):
                            current = int(st.session_state.get(score_key, 0))

                            if label == "C":
                                st.session_state[score_key] = 0

                            elif label == "←":
                                txt = str(current)

                                if len(txt) <= 1:
                                    st.session_state[score_key] = 0
                                else:
                                    st.session_state[score_key] = int(txt[:-1])

                            elif label == "+":
                                st.session_state[score_key] = min(current + 1, 50)

                            elif label == "-":
                                st.session_state[score_key] = max(current - 1, 0)

                            else:
                                digit = label

                                if current == 0:
                                    new_value = int(digit)
                                else:
                                    new_value = int(str(current) + digit)

                                st.session_state[score_key] = min(new_value, 50)

                            st.rerun()

        st.markdown(
            f"""
### {country_flag(match.get("team1_code", ""))} {team1}
### {country_flag(match.get("team2_code", ""))} {team2}
            """
        )

        col1, col2 = st.columns(2, gap="medium")

        with col1:
            keypad(score1_key, team1)

        with col2:
            keypad(score2_key, team2)

        score1 = int(st.session_state.get(score1_key, 0))
        score2 = int(st.session_state.get(score2_key, 0))

        final_prediction = result_from_score(score1, score2)

        st.info(f"Deze score telt als pronostiek: **{final_prediction}**")

        b1, b2 = st.columns(2, gap="small")

        with b1:
            if st.button("✅ Opslaan", use_container_width=True, type="primary"):
                st.session_state.score_predictions[match_id] = {
                    "prediction": final_prediction,
                    "score1": score1,
                    "score2": score2,
                }

                st.session_state[f"score_pred_{match_id}"] = final_prediction
                st.session_state.pending_score_match_id = ""
                st.session_state.pending_score_choice = ""

                if score1_key in st.session_state:
                    del st.session_state[score1_key]

                if score2_key in st.session_state:
                    del st.session_state[score2_key]

                st.rerun()

        with b2:
            if st.button("❌ Annuleren", use_container_width=True):
                st.session_state.pending_score_match_id = ""
                st.session_state.pending_score_choice = ""

                if score1_key in st.session_state:
                    del st.session_state[score1_key]

                if score2_key in st.session_state:
                    del st.session_state[score2_key]

                st.rerun()

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

    matches_by_id = {}

    st.write("")

    for _, match in wedstrijden.iterrows():

        match_id = str(
            match.get("match_id", "")
        ).strip()

        if not match_id:
            continue

        matches_by_id[match_id] = match

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

        pred_key = f"score_pred_{match_id}"
        score_text = get_score_text(match_id)

        with st.container(
            key=f"score_match_card_{match_id}"
        ):

            col_info, col_pred = st.columns(
                [1.9, 1],
                gap="small",
            )

            with col_info:

                score_html = ""

                if score_text:
                    score_html = f'<div class="score-pill">🎯 {score_text}</div>'

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

{score_html}
                    """,
                    unsafe_allow_html=True,
                )

            with col_pred:

                kwargs = {
                    "label": "Pronostiek",
                    "options": ["1", "X", "2"],
                    "key": pred_key,
                    "label_visibility": "collapsed",
                    "on_change": prediction_clicked,
                    "args": (match_id,),
                }

                if pred_key not in st.session_state:
                    kwargs["default"] = get_prediction(match_id)

                st.segmented_control(**kwargs)

    pending_match_id = str(st.session_state.get("pending_score_match_id", "")).strip()

    if pending_match_id and pending_match_id in matches_by_id:
        score_dialog(matches_by_id[pending_match_id])
