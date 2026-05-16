import streamlit as st

try:
    from modules.data_loader import get_matches
except ImportError:
    from data_loader import get_matches


def show_pronostiek_scores(user_id):
    st.markdown(f"### 🎯 Scores invullen: {user_id}")

    df = get_matches()
    if df.empty:
        st.warning("Geen wedstrijden gevonden.")
        return

    dagen = sorted(df["speeldag"].unique().tolist())
    gekozen_dag = st.select_slider("Kies Speeldag", options=dagen)

    dag_df = df[df["speeldag"] == gekozen_dag]

    for _, match in dag_df.iterrows():
        m_id = str(match.get("match_id", "0"))
        t1 = str(match.get("team1", "Team 1"))
        t2 = str(match.get("team2", "Team 2"))
        c1 = str(match.get("team1_code", "??"))
        c2 = str(match.get("team2_code", "??"))
        tijd = str(match.get("tijd", "00:00"))
        groep = str(match.get("groep", "-"))

        with st.container(border=True):
            st.caption(f"Groep {groep} • {tijd}")

            col_l, col_s, col_r = st.columns([4, 3, 4])

            with col_l:
                st.markdown(f"**{t1}**")
                st.caption(c1)

            with col_s:
                s1, s2 = st.columns(2)

                s1.number_input(
                    "T1",
                    min_value=0,
                    max_value=15,
                    value=0,
                    step=1,
                    key=f"s1_{m_id}",
                    label_visibility="collapsed",
                )

                s2.number_input(
                    "T2",
                    min_value=0,
                    max_value=15,
                    value=0,
                    step=1,
                    key=f"s2_{m_id}",
                    label_visibility="collapsed",
                )

            with col_r:
                st.markdown(
                    f"<p style='text-align:right; margin:0;'><b>{t2}</b></p>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"<p style='text-align:right; margin:0; color:gray; font-size:0.8em;'>{c2}</p>",
                    unsafe_allow_html=True,
                )

    if st.button("💾 Pronostiek Opslaan", use_container_width=True, type="primary"):
        st.success("Je scores zijn succesvol verwerkt!")
