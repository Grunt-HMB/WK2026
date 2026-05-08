import streamlit as st
from modules.database import update_or_append_result
from modules.utils import safe_int, flag_emoji

def show_admin_results(matches_df, results_df):
    st.markdown('<div class="main-title">Admin - uitslagen</div>', unsafe_allow_html=True)

    groups = ["Alle"] + sorted([str(g) for g in matches_df["groep"].dropna().unique()])
    selected_group = st.selectbox("Filter", groups)

    view = matches_df.copy()

    if selected_group != "Alle":
        view = view[view["groep"].astype(str) == selected_group]

    view = view.sort_values(["datum", "tijd", "match_id"], kind="stable")

    for _, match in view.iterrows():
        match_id = str(match["match_id"])
        team1 = str(match.get("team1", ""))
        team2 = str(match.get("team2", ""))

        existing = results_df[results_df["match_id"].astype(str) == match_id] if not results_df.empty else None

        default1 = 0
        default2 = 0

        if existing is not None and not existing.empty:
            default1 = safe_int(existing.iloc[0].get("real_team1")) or 0
            default2 = safe_int(existing.iloc[0].get("real_team2")) or 0

        with st.container(border=True):
            st.subheader(f"{flag_emoji(match.get('team1_code', ''))} {team1} - {flag_emoji(match.get('team2_code', ''))} {team2}")

            c1, c2 = st.columns(2)
            with c1:
                real1 = st.number_input(team1, min_value=0, max_value=30, value=default1, key=f"admin_r1_{match_id}")
            with c2:
                real2 = st.number_input(team2, min_value=0, max_value=30, value=default2, key=f"admin_r2_{match_id}")

            if st.button("Uitslag opslaan", key=f"save_result_{match_id}"):
                update_or_append_result(match_id, real1, real2)
                st.success("Uitslag opgeslagen.")
                st.rerun()
