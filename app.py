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
    layout="centered",
    initial_sidebar_state="collapsed",
)

USER_ID = "Tom"


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


def get_prediction(match_id):
    data = st.session_state.local_predictions.get(str(match_id), "X")

    if isinstance(data, dict):
        value = data.get("prediction", "X")
    else:
        value = data

    value = str(value).upper().strip()
    return value if value in ["1", "X", "2"] else "X"


def prediction_changed(match_id):
    key = f"pred_{match_id}"
    value = st.session_state.get(key, "X")

    st.session_state.local_predictions[str(match_id)] = {
        "prediction": value,
        "score1": "",
        "score2": "",
    }


def save_all_predictions():
    saved = batch_save_predictions(
        user_id=USER_ID,
        local_predictions=st.session_state.local_predictions,
        status="concept",
    )
    st.cache_data.clear()
    return saved


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
    padding: 0.45rem 0.55rem 0.55rem 0.55rem !important;
    border-bottom: 1px solid rgba(255,255,255,0.12);
}

.st-key-top_bar > div {
    max-width: 820px;
    margin-left: auto;
    margin-right: auto;
}

.top-spacer {
    height: 178px;
}

.st-key-top_bar div[data-testid="stAlert"] {
    padding: 0.38rem 0.6rem !important;
    font-size: 0.76rem !important;
    margin-bottom: 0.25rem !important;
    border-radius: 10px !important;
}

.st-key-top_bar button {
    min-height: 36px !important;
    height: 36px !important;
    border-radius: 10px !important;
    font-weight: 800 !important;
}

[class*="st-key-match_card_"] {
    background: #111827;
    border: 1px solid rgba(255,255,255,0.13);
    border-radius: 14px;
    padding: 0.65rem !important;
    margin-bottom: 0.55rem;
}

[class*="st-key-match_card_"] p {
    margin-bottom: 0 !important;
    line-height: 1.25 !important;
}

[class*="st-key-match_card_"] div[data-testid="stSegmentedControl"] {
    margin-top: 0.45rem !important;
}

[class*="st-key-match_card_"] div[data-testid="stSegmentedControl"] button {
    min-width: 52px !important;
    height: 34px !important;
    padding: 0 !important;
    font-weight: 800 !important;
}

footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)


if "page" not in st.session_state:
    st.session_state.page = "Wedstrijden"

if "local_predictions" not in st.session_state:
    st.session_state.local_predictions = {}

if "loaded_predictions" not in st.session_state:
    st.session_state.loaded_predictions = False


@st.cache_data(ttl=60)
def get_data():
    return load_matches(), load_predictions(USER_ID)


matches_df, predictions_df = get_data()


if not st.session_state.loaded_predictions:
    if not predictions_df.empty:
        for _, row in predictions_df.iterrows():
            match_id = str(row.get("match_id", "")).strip()
            if not match_id:
                continue

            prediction = str(row.get("prediction", "X")).upper().strip()
            if prediction not in ["1", "X", "2"]:
                prediction = "X"

            st.session_state.local_predictions[match_id] = {
                "prediction": prediction,
                "score1": row.get("score1", ""),
                "score2": row.get("score2", ""),
            }

    st.session_state.loaded_predictions = True


with st.container(key="top_bar"):
    st.info("Kies uitslagen en druk OPSLAAN.", icon="⚡")

    if st.button("💾 NU ALLES OPSLAAN", use_container_width=True, type="primary"):
        saved = save_all_predictions()
        st.success(f"Opgeslagen: {saved} wedstrijden")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        if st.button("⚽", use_container_width=True):
            st.session_state.page = "Wedstrijden"
            st.rerun()

    with c2:
        if st.button("📊", use_container_width=True):
            st.session_state.page = "Stand"
            st.rerun()

    with c3:
        if st.button("🏆", use_container_width=True):
            st.session_state.page = "KO"
            st.rerun()

    with c4:
        if st.button("👤", use_container_width=True):
            st.session_state.page = "Mijn"
            st.rerun()


st.markdown('<div class="top-spacer"></div>', unsafe_allow_html=True)


if st.session_state.page == "Wedstrijden":

    wedstrijden = matches_df.copy()

    if wedstrijden.empty:
        st.warning("Geen wedstrijden gevonden.")
    else:
        wedstrijden["match_id"] = wedstrijden["match_id"].astype(str).str.strip()

        if "ronde" in wedstrijden.columns:
            wedstrijden = wedstrijden[
                wedstrijden["ronde"].astype(str).str.lower().str.contains("groep", na=False)
            ].copy()

        sort_cols = [c for c in ["datum", "tijd", "match_id"] if c in wedstrijden.columns]
        if sort_cols:
            wedstrijden = wedstrijden.sort_values(sort_cols, kind="stable")

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

            if pred_key not in st.session_state:
                st.session_state[pred_key] = get_prediction(match_id)

            with st.container(key=f"match_card_{match_id}"):

                col_date, col_match = st.columns([0.75, 2.6], gap="small")

                with col_date:
                    st.markdown(f"**{datum}**  \n{tijd}  \n🟢")

                with col_match:
                    st.markdown(
                        f"**{country_flag(team1_code)} {team1}**  \n"
                        f"**{country_flag(team2_code)} {team2}**"
                    )

                st.segmented_control(
                    "Pronostiek",
                    ["1", "X", "2"],
                    key=pred_key,
                    label_visibility="collapsed",
                    on_change=prediction_changed,
                    args=(match_id,),
                )


elif st.session_state.page == "Stand":
    st.subheader("📊 Standen")
    st.write("Hier komen de groepsstanden.")


elif st.session_state.page == "KO":
    st.subheader("🏆 Knockout")
    st.write("Hier komt het knockoutschema.")


elif st.session_state.page == "Mijn":
    st.subheader("👤 Mijn pronostiek")

    rows = []

    for match_id, data in st.session_state.local_predictions.items():
        if isinstance(data, dict):
            prediction = data.get("prediction", "")
        else:
            prediction = data

        rows.append({
            "match_id": match_id,
            "pronostiek": prediction,
        })

    if rows:
        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("Nog geen voorspellingen gekozen.")