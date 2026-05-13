import streamlit as st
import pandas as pd

from modules.database import (
    load_matches,
    load_predictions,
    batch_save_predictions,
)

st.set_page_config(
    page_title="WK 2026",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed",
)

USER_ID = "Tom"

st.markdown("""
<style>
.block-container {
    padding-top: 0 !important;
    padding-left: 0.4rem !important;
    padding-right: 0.4rem !important;
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
    padding: 0.4rem 0.55rem 0.55rem 0.55rem !important;
    border-bottom: 1px solid rgba(255,255,255,0.12);
}

.st-key-top_bar > div {
    max-width: 900px;
    margin-left: auto;
    margin-right: auto;
}

.top-spacer {
    height: 170px;
}

.st-key-top_bar div[data-testid="stAlert"] {
    padding: 0.45rem 0.7rem !important;
    font-size: 0.82rem !important;
}

.st-key-top_bar button {
    height: 40px !important;
    min-height: 40px !important;
    border-radius: 11px !important;
    font-weight: 800 !important;
}

div[data-testid="stDataFrame"] {
    font-size: 0.8rem !important;
}

@media (max-width: 480px) {
    .top-spacer {
        height: 165px;
    }
}
</style>
""", unsafe_allow_html=True)


def country_flag(code):
    code = str(code or "").strip().upper()

    if len(code) != 2:
        return ""

    return chr(ord(code[0]) + 127397) + chr(ord(code[1]) + 127397)


if "menu_keuze" not in st.session_state:
    st.session_state.menu_keuze = "⚽ Wedstrijden"

if "local_predictions" not in st.session_state:
    st.session_state.local_predictions = {}

if "loaded_predictions" not in st.session_state:
    st.session_state.loaded_predictions = False


@st.cache_data(ttl=60)
def get_matches_cached():
    return load_matches()


@st.cache_data(ttl=60)
def get_predictions_cached(user_id):
    return load_predictions(user_id)


matches_df = get_matches_cached()
predictions_df = get_predictions_cached(USER_ID)


if not st.session_state.loaded_predictions:

    if not predictions_df.empty:

        for _, row in predictions_df.iterrows():

            match_id = str(row.get("match_id", "")).strip()

            if match_id:
                st.session_state.local_predictions[match_id] = {
                    "prediction": str(row.get("prediction", "")).upper().strip(),
                    "score1": row.get("score1", ""),
                    "score2": row.get("score2", ""),
                }

    st.session_state.loaded_predictions = True


with st.container(key="top_bar"):

    st.info(
        "Wijzigingen blijven lokaal. Klik op OPSLAAN om alles te bewaren.",
        icon="💾",
    )

    if st.button("OPSLAAN", use_container_width=True, type="primary"):

        saved = batch_save_predictions(
            user_id=USER_ID,
            local_predictions=st.session_state.local_predictions,
            status="concept",
        )

        get_predictions_cached.clear()

        st.success(f"Opgeslagen: {saved} wedstrijden.")

    st.radio(
        "Menu",
        [
            "⚽ Wedstrijden",
            "📊 Standen",
            "🏆 Knockout",
            "👤 Mijn",
        ],
        key="menu_keuze",
        horizontal=True,
        label_visibility="collapsed",
    )


st.markdown('<div class="top-spacer"></div>', unsafe_allow_html=True)


if st.session_state.menu_keuze == "⚽ Wedstrijden":

    wedstrijden = matches_df.copy()

    if wedstrijden.empty:
        st.warning("Geen wedstrijden gevonden.")

    else:

        wedstrijden["match_id"] = wedstrijden["match_id"].astype(str).str.strip()

        rows = []

        for _, match in wedstrijden.iterrows():

            match_id = str(match.get("match_id", "")).strip()

            if not match_id:
                continue

            datum = str(match.get("datum", "")).strip()
            tijd = str(match.get("tijd", "")).strip()

            team1 = str(match.get("team1", "")).strip()
            team2 = str(match.get("team2", "")).strip()

            team1_code = str(match.get("team1_code", "")).strip()
            team2_code = str(match.get("team2_code", "")).strip()

            prediction_data = st.session_state.local_predictions.get(match_id, {})
            prediction = ""

            if isinstance(prediction_data, dict):
                prediction = str(prediction_data.get("prediction", "")).upper().strip()
            else:
                prediction = str(prediction_data).upper().strip()

            if prediction not in ["1", "X", "2"]:
                prediction = "X"

            rows.append({
                "match_id": match_id,
                "Datum": datum,
                "Tijd": tijd,
                "Status": "🟢 Open",
                "Wedstrijd": (
                    f"{country_flag(team1_code)} {team1} "
                    f"vs "
                    f"{country_flag(team2_code)} {team2}"
                ),
                "Pronostiek": prediction,
            })

        editor_df = pd.DataFrame(rows)

        edited_df = st.data_editor(
            editor_df,
            hide_index=True,
            use_container_width=True,
            height=620,
            disabled=[
                "match_id",
                "Datum",
                "Tijd",
                "Status",
                "Wedstrijd",
            ],
            column_config={
                "match_id": None,
                "Datum": st.column_config.TextColumn(
                    "Datum",
                    width="small",
                ),
                "Tijd": st.column_config.TextColumn(
                    "Tijd",
                    width="small",
                ),
                "Status": st.column_config.TextColumn(
                    "Status",
                    width="small",
                ),
                "Wedstrijd": st.column_config.TextColumn(
                    "Wedstrijd",
                    width="medium",
                ),
                "Pronostiek": st.column_config.SelectboxColumn(
                    "1/X/2",
                    options=["1", "X", "2"],
                    required=True,
                    width="small",
                ),
            },
            key="wedstrijden_editor",
        )

        for _, row in edited_df.iterrows():

            match_id = str(row["match_id"]).strip()
            prediction = str(row["Pronostiek"]).upper().strip()

            st.session_state.local_predictions[match_id] = {
                "prediction": prediction,
                "score1": "",
                "score2": "",
            }


elif st.session_state.menu_keuze == "📊 Standen":

    st.subheader("📊 Standen")
    st.write("Hier komen de groepsstanden.")


elif st.session_state.menu_keuze == "🏆 Knockout":

    st.subheader("🏆 Knockout")
    st.write("Hier komt het knockoutschema.")


elif st.session_state.menu_keuze == "👤 Mijn":

    st.subheader("👤 Mijn pronostiek")
    st.write(st.session_state.local_predictions)