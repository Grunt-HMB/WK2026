import streamlit as st
import pandas as pd

from modules.database import (
    load_matches,
    load_predictions,
    batch_save_predictions,
)


def show_pronostiek(user_id="Tom", standings_df=None):

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

    def get_prediction(match_id):
        data = st.session_state.local_predictions.get(
            str(match_id),
            "",
        )

        if isinstance(data, dict):
            value = data.get("prediction", "")
        else:
            value = data

        value = str(value).upper().strip()

        return value if value in ["1", "X", "2"] else None

    def prediction_changed(match_id):
        key = f"pred_{match_id}"

        value = st.session_state.get(key, None)

        if value in ["1", "X", "2"]:
            st.session_state.local_predictions[str(match_id)] = {
                "prediction": value,
                "score1": "",
                "score2": "",
            }

        else:
            st.session_state.local_predictions.pop(
                str(match_id),
                None,
            )

    def save_all_predictions():
        saved = batch_save_predictions(
            user_id=user_id,
            local_predictions=st.session_state.local_predictions,
            status="concept",
        )

        st.cache_data.clear()

        return saved

    # =========================================================
    # SESSION STATE
    # =========================================================

    if "local_predictions" not in st.session_state:
        st.session_state.local_predictions = {}

    loaded_key = f"loaded_predictions_{user_id}"

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

    .st-key-top_bar {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        z-index: 999999 !important;
        background: #0e1117 !important;
        padding: 0.35rem 0.5rem 0.45rem 0.5rem !important;
        border-bottom: 1px solid rgba(255,255,255,0.12);
    }

    .st-key-top_bar > div {
        max-width: 820px;
        margin-left: auto;
        margin-right: auto;
    }

    .top-spacer {
        height: 78px;
    }

    .st-key-save_button button {
        min-height: 34px !important;
        height: 34px !important;
        border-radius: 10px !important;
        font-size: 0.82rem !important;
        font-weight: 900 !important;
    }

    [class*="st-key-match_card_"] {
        background: #111827;
        border: 1px solid rgba(255,255,255,0.13);
        border-radius: 14px;
        padding: 0.55rem !important;
        margin-bottom: 0.5rem;
    }

    [class*="st-key-match_card_"] p {
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

    [class*="st-key-match_card_"] div[data-testid="stSegmentedControl"] {
        margin-top: 0.35rem !important;
    }

    [class*="st-key-match_card_"] div[data-testid="stSegmentedControl"] button {
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

                match_id = str(
                    row.get("match_id", "")
                ).strip()

                if not match_id:
                    continue

                prediction = str(
                    row.get("prediction", "")
                ).upper().strip()

                if prediction in ["1", "X", "2"]:

                    st.session_state.local_predictions[match_id] = {
                        "prediction": prediction,
                        "score1": row.get("score1", ""),
                        "score2": row.get("score2", ""),
                    }

        st.session_state[loaded_key] = True

    # =========================================================
    # TOP BAR
    # =========================================================

    with st.container(key="top_bar"):

        col_home, col_save = st.columns(
            [1, 1.4],
            gap="small",
        )

        with col_home:

            if st.button(
                "☰ Hoofdmenu",
                key="back_to_main_menu",
                use_container_width=True,
            ):
                st.session_state.main_page = "🏠 Hoofdmenu"
                st.rerun()

        with col_save:

            if st.button(
                "💾 OPSLAAN",
                key="save_button",
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

    st.write("")

    for _, match in wedstrijden.iterrows():

        match_id = str(
            match.get("match_id", "")
        ).strip()

        if not match_id:
            continue

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

        pred_key = f"pred_{match_id}"

        with st.container(
            key=f"match_card_{match_id}"
        ):

            col_info, col_pred = st.columns(
                [1.9, 1],
                gap="small",
            )

            with col_info:

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

            with col_pred:

                kwargs = {
                    "label": "Pronostiek",
                    "options": ["1", "X", "2"],
                    "key": pred_key,
                    "label_visibility": "collapsed",
                    "on_change": prediction_changed,
                    "args": (match_id,),
                }

                if pred_key not in st.session_state:
                    kwargs["default"] = get_prediction(match_id)

                st.segmented_control(**kwargs)
