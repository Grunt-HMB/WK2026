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

st.markdown("""
<style>
.block-container {
    max-width: 720px;
    padding-top: 0 !important;
    padding-left: 0.35rem !important;
    padding-right: 0.35rem !important;
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
    padding: 0.3rem 0.5rem 0.4rem 0.5rem !important;
    border-bottom: 1px solid rgba(255,255,255,0.12);
}

.st-key-top_bar > div {
    max-width: 720px;
    margin-left: auto;
    margin-right: auto;
}

.top-spacer {
    height: 145px;
}

.st-key-top_bar div[data-testid="stAlert"] {
    padding: 0.32rem 0.5rem !important;
    font-size: 0.75rem !important;
    margin-bottom: 0.2rem !important;
    border-radius: 10px !important;
}

.st-key-top_bar button {
    height: 36px !important;
    min-height: 36px !important;
    border-radius: 10px !important;
    font-weight: 800 !important;
}

.st-key-menu_keuze div[role="radiogroup"] {
    display: flex !important;
    flex-direction: row !important;
    justify-content: space-between !important;
}

.st-key-menu_keuze label[data-baseweb="radio"] {
    background: transparent !important;
    border: none !important;
    padding: 0.05rem !important;
}

.st-key-menu_keuze label[data-baseweb="radio"] > div:first-child {
    display: none !important;
}

.st-key-menu_keuze label[data-baseweb="radio"] span {
    font-size: 0.76rem !important;
    font-weight: 800 !important;
}

.match-card {
    background: #111827;
    border: 1px solid rgba(255,255,255,0.13);
    border-radius: 13px;
    padding: 0.55rem;
    margin-bottom: 0.55rem;
}

.match-line {
    font-size: 0.82rem;
    line-height: 1.35;
    font-weight: 800;
}

.match-meta {
    color: #cbd5e1;
    font-size: 0.72rem;
    margin-bottom: 0.25rem;
}

.match-card div[data-testid="stSegmentedControl"] button {
    min-width: 42px !important;
    height: 32px !important;
    padding: 0 !important;
    font-weight: 800 !important;
}

div[data-testid="stVerticalBlock"] {
    gap: 0.35rem !important;
}

footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)


def country_flag(code):
    code = str(code or "").strip().upper()
    if len(code) != 2:
        return ""
    return chr(ord(code[0]) + 127397) + chr(ord(code[1]) + 127397)


def normalize_time(value):
    txt = str(value or "").strip()
    if txt.endswith(":00") and txt.count(":") == 2:
        txt = txt[: txt.rfind(":")]
    return txt


def compact_date(value):
    txt = str(value or "").strip()
    parts = txt.split("-")
    if len(parts) >= 2:
        return f"{parts[0]}/{parts[1]}"
    return txt


def get_existing_prediction(match_id):
    data = st.session_state.local_predictions.get(str(match_id), {})
    value = data.get("prediction", "") if isinstance(data, dict) else data
    value = str(value).upper().strip()
    return value if value in ["1", "X", "2"] else "X"


def prediction_changed(match_id):
    key = f"pred_{match_id}"
    prediction = st.session_state.get(key, "X")

    st.session_state.local_predictions[str(match_id)] = {
        "prediction": prediction,
        "score1": "",
        "score2": "",
    }


if "menu_keuze" not in st.session_state:
    st.session_state.menu_keuze = "⚽ Wedstr."

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
    st.info("Lokaal bewaard. Druk OPSLAAN.", icon="💾")

    if st.button("OPSLAAN", use_container_width=True, type="primary"):
        saved = batch_save_predictions(
            user_id=USER_ID,
            local_predictions=st.session_state.local_predictions,
            status="concept",
        )
        get_predictions_cached.clear()
        st.success(f"Opgeslagen: {saved}")

    st.radio(
        "Menu",
        ["⚽ Wedstr.", "📊 Stand", "🏆 KO", "👤 Mijn"],
        key="menu_keuze",
        horizontal=True,
        label_visibility="collapsed",
    )


st.markdown('<div class="top-spacer"></div>', unsafe_allow_html=True)


if st.session_state.menu_keuze == "⚽ Wedstr.":

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

            datum = compact_date(match.get("datum", ""))
            tijd = normalize_time(match.get("tijd", ""))

            team1 = str(match.get("team1", "")).strip()
            team2 = str(match.get("team2", "")).strip()
            team1_code = str(match.get("team1_code", "")).strip()
            team2_code = str(match.get("team2_code", "")).strip()

            key = f"pred_{match_id}"

            if key not in st.session_state:
                st.session_state[key] = get_existing_prediction(match_id)

            st.markdown('<div class="match-card">', unsafe_allow_html=True)

            st.markdown(
                f"""
                <div class="match-meta">
                    <b>{datum}</b> &nbsp; {tijd} &nbsp; 🟢
                </div>
                <div class="match-line">
                    {country_flag(team1_code)} {team1} vs {country_flag(team2_code)} {team2}
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.segmented_control(
                "Pronostiek",
                ["1", "X", "2"],
                key=key,
                label_visibility="collapsed",
                on_change=prediction_changed,
                args=(match_id,),
            )

            st.markdown("</div>", unsafe_allow_html=True)


elif st.session_state.menu_keuze == "📊 Stand":
    st.subheader("📊 Standen")
    st.write("Hier komen de groepsstanden.")


elif st.session_state.menu_keuze == "🏆 KO":
    st.subheader("🏆 Knockout")
    st.write("Hier komt het knockoutschema.")


elif st.session_state.menu_keuze == "👤 Mijn":
    st.subheader("👤 Mijn pronostiek")

    mijn_rows = []

    for match_id, data in st.session_state.local_predictions.items():
        prediction = data.get("prediction", "") if isinstance(data, dict) else data

        mijn_rows.append({
            "match_id": match_id,
            "pronostiek": prediction,
        })

    if not mijn_rows:
        st.info("Nog geen pronostieken gekozen.")
    else:
        st.dataframe(
            pd.DataFrame(mijn_rows),
            use_container_width=True,
            hide_index=True,
        )