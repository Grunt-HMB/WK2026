import streamlit as st

from modules.database import update_or_append_result


def flag_img(code):
    code = str(code or "").strip().lower()

    if len(code) != 2:
        return ""

    return f"https://flagcdn.com/w40/{code}.png"


def get_existing_result(results_df, match_id):
    if results_df.empty:
        return 0, 0

    found = results_df[
        results_df["match_id"].astype(str).str.strip() == str(match_id)
    ]

    if found.empty:
        return 0, 0

    row = found.iloc[0]

    try:
        real1 = int(row.get("real_team1", 0))
    except Exception:
        real1 = 0

    try:
        real2 = int(row.get("real_team2", 0))
    except Exception:
        real2 = 0

    return real1, real2


def show_admin_results(matches_df, results_df):
    st.markdown("### Admin - uitslagen")

    if matches_df.empty:
        st.info("Geen wedstrijden gevonden.")
        return

    matches = matches_df.copy()

    matches["match_id_sort"] = matches["match_id"].astype(str).str.extract(r"(\d+)").fillna(0).astype(int)
    matches = matches.sort_values("match_id_sort")

    filters = ["Alle"] + sorted(matches["ronde"].dropna().astype(str).unique().tolist())
    selected_filter = st.selectbox("Filter", filters)

    if selected_filter != "Alle":
        matches = matches[matches["ronde"].astype(str) == selected_filter]

    st.caption("Vul achteraan de uitslag in en klik per wedstrijd op Opslaan.")

    for _, match in matches.iterrows():
        match_id = str(match.get("match_id", ""))

        team1 = str(match.get("team1", ""))
        team2 = str(match.get("team2", ""))

        real1, real2 = get_existing_result(results_df, match_id)

        with st.container(border=True):
            col_id, col_date, col_match, col_s1, col_sep, col_s2, col_save = st.columns(
                [0.45, 1.15, 4.8, 0.75, 0.2, 0.75, 1.0],
                gap="small",
            )

            with col_id:
                st.markdown(f"**#{match_id}**")

            with col_date:
                st.caption(str(match.get("ronde", "")))
                st.markdown(
                    f"""
                    <div style="font-size:0.82rem;font-weight:800;color:#64748b;">
                    {match.get("datum", "")}<br>{match.get("tijd", "")}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with col_match:
                f1 = flag_img(match.get("team1_code", ""))
                f2 = flag_img(match.get("team2_code", ""))

                c1, c2, c3, c4, c5 = st.columns([0.25, 1.4, 0.12, 0.25, 1.4], gap="small")

                with c1:
                    if f1:
                        st.image(f1, width=28)

                with c2:
                    st.markdown(f"**{team1}**")

                with c3:
                    st.markdown("**-**")

                with c4:
                    if f2:
                        st.image(f2, width=28)

                with c5:
                    st.markdown(f"**{team2}**")

                st.caption(str(match.get("speelstad", "")))

            with col_s1:
                score1 = st.number_input(
                    "T1",
                    min_value=0,
                    max_value=50,
                    value=real1,
                    step=1,
                    key=f"admin_score1_{match_id}",
                    label_visibility="collapsed",
                )

            with col_sep:
                st.markdown("**-**")

            with col_s2:
                score2 = st.number_input(
                    "T2",
                    min_value=0,
                    max_value=50,
                    value=real2,
                    step=1,
                    key=f"admin_score2_{match_id}",
                    label_visibility="collapsed",
                )

            with col_save:
                if st.button(
                    "Opslaan",
                    key=f"admin_save_{match_id}",
                    use_container_width=True,
                ):
                    update_or_append_result(match_id, score1, score2)
                    st.success(f"Uitslag #{match_id} opgeslagen.")
                    st.rerun()
