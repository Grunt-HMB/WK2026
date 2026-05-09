import streamlit as st

from modules.styles import inject_css
from modules.database import ensure_sheets_exist, load_all_data, load_sheet
from modules.auth import show_sidebar
from modules.predictions import show_group_phase
from modules.views import show_my_predictions, show_scoreboard, show_rules
from modules.admin import show_admin_results
from modules.wedstrijden import show_wedstrijden


st.set_page_config(
    page_title="WK 2026 Pronostiek",
    page_icon="⚽",
    layout="wide",
)

inject_css()


def normalize_columns(df):
    if df is None:
        return None

    df = df.copy()
    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.lower()
    )
    return df


try:
    ensure_sheets_exist()
    data = load_all_data()

    users_df = normalize_columns(data["users"])
    matches_df = normalize_columns(data["matches"])
    predictions_df = normalize_columns(data["predictions"])
    results_df = normalize_columns(data["results"])

    standings_df = data.get("standings")
    standings_df = normalize_columns(standings_df) if standings_df is not None else None

    try:
        wedstrijden_df = load_sheet("Wedstrijden")
        wedstrijden_df = normalize_columns(wedstrijden_df)

        required_cols = ["datum", "tijd", "match_id_sort"]

        missing_cols = [
            col for col in required_cols
            if col not in wedstrijden_df.columns
        ]

        if missing_cols:
            st.error(
                "Het tabblad 'Wedstrijden' mist deze kolommen: "
                + ", ".join(missing_cols)
            )
            st.write("Gevonden kolommen:", wedstrijden_df.columns.tolist())
            st.stop()

    except Exception as e:
        st.error("Fout bij laden van tabblad 'Wedstrijden'.")
        st.exception(e)
        wedstrijden_df = None

except Exception as e:
    st.error("Fout bij laden van Google Sheets.")
    st.exception(e)
    st.stop()


user = show_sidebar(users_df)

if not user:
    st.markdown(
        '<div class="main-title">⚽ WK 2026 Pronostiek</div>',
        unsafe_allow_html=True,
    )
    st.info("Log in of registreer via de zijbalk.")
    st.stop()


is_admin = str(user.get("admin", "")).upper() == "TRUE"

menu_items = [
    "Groepsfase",
    "Wedstrijden",
    "Mijn voorspellingen",
    "Scorebord",
    "Reglement",
]

if is_admin:
    menu_items.append("Admin - uitslagen")

menu = st.sidebar.radio("Menu", menu_items)


if menu == "Groepsfase":
    show_group_phase(
        user,
        matches_df,
        predictions_df,
        standings_df,
    )

elif menu == "Wedstrijden":
    if wedstrijden_df is None:
        st.error("Het tabblad 'Wedstrijden' kon niet geladen worden.")
    else:
        show_wedstrijden(
            user,
            wedstrijden_df,
            predictions_df,
        )

elif menu == "Mijn voorspellingen":
    show_my_predictions(
        user,
        matches_df,
        predictions_df,
    )

elif menu == "Scorebord":
    show_scoreboard(
        users_df,
        matches_df,
        predictions_df,
        results_df,
    )

elif menu == "Reglement":
    show_rules()

elif menu == "Admin - uitslagen":
    show_admin_results(
        matches_df,
        results_df,
    )


st.markdown(
    '<div class="footer-line">WK 2026 Pronostiek © 2026</div>',
    unsafe_allow_html=True,
)
