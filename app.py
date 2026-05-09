import streamlit as st

from modules.styles import inject_css
from modules.database import ensure_sheets_exist, load_all_data
from modules.auth import show_sidebar
from modules.predictions import show_group_phase
from modules.views import show_my_predictions, show_scoreboard, show_rules
from modules.admin import show_admin_results


st.set_page_config(
    page_title="WK 2026 Pronostiek",
    page_icon="⚽",
    layout="wide",
)

inject_css()

try:
    ensure_sheets_exist()

    data = load_all_data()

    st.write("STANDEN TEST")
    st.dataframe(data["standings"])

    st.write("BESTE DERDEN TEST")
    st.dataframe(data["best_thirds"])

    st.write("MATCHES TEST")
    st.dataframe(data["matches"])

except Exception as e:
    st.error("Fout bij laden van Google Sheets.")
    st.exception(e)
    st.stop()

users_df = data["users"]
matches_df = data["matches"]
predictions_df = data["predictions"]
results_df = data["results"]

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
    "Mijn voorspellingen",
    "Scorebord",
    "Reglement",
]

if is_admin:
    menu_items.append("Admin - uitslagen")

menu = st.sidebar.radio("Menu", menu_items)

if menu == "Groepsfase":
    show_group_phase(user, matches_df, predictions_df, data["standings"])

elif menu == "Mijn voorspellingen":
    show_my_predictions(user, matches_df, predictions_df)

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
    show_admin_results(matches_df, results_df)

st.markdown(
    '<div class="footer-line">WK 2026 Pronostiek © 2026</div>',
    unsafe_allow_html=True,
)
