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

            col_l, col_s, col_r = st.columns([5, 3, 5])

            with col_l:

                st.markdown(
                    f"""
                    <div style="
                        display:flex;
                        align-items:center;
                        gap:8px;
                    ">
                        <img src="https://flagcdn.com/w40/{c1.lower()}.png"
                             width="28">

                        <div>
                            <div style="font-weight:700;">
                                {t1}
                            </div>

                            <div style="
                                color:gray;
                                font-size:12px;
                            ">
                                {c1}
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

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
                    f"""
                    <div style="
                        display:flex;
                        align-items:center;
                        gap:8px;
                    ">
                        <img src="https://flagcdn.com/w40/{c2.lower()}.png"
                             width="28">

                        <div>
                            <div style="font-weight:700;">
                                {t2}
                            </div>

                            <div style="
                                color:gray;
                                font-size:12px;
                            ">
                                {c2}
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
