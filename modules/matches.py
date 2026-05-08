import streamlit as st

def show_matches(user):
    st.subheader(f"Ingelogd als: {user}")

    wedstrijden = [
        ("België", "Canada"),
        ("Mexico", "Japan"),
        ("Frankrijk", "Brazilië"),
    ]

    if "predictions" not in st.session_state:
        st.session_state.predictions = {}

    for idx, (team1, team2) in enumerate(wedstrijden, start=1):

        st.markdown(f"### 🇧🇪 {team1} - 🇨🇦 {team2}")

        cols = st.columns(4)

        if cols[0].button("1", key=f"1_{idx}"):
            st.session_state.predictions[idx] = "1"

        if cols[1].button("X", key=f"x_{idx}"):
            st.session_state.predictions[idx] = "X"

        if cols[2].button("2", key=f"2_{idx}"):
            st.session_state.predictions[idx] = "2"

        if cols[3].button("⚽", key=f"s_{idx}"):
            st.session_state[f"show_score_{idx}"] = True

        if st.session_state.get(f"show_score_{idx}", False):
            c1, c2 = st.columns(2)

            with c1:
                score1 = st.number_input(
                    f"Goals {team1}",
                    min_value=0,
                    max_value=20,
                    key=f"score1_{idx}"
                )

            with c2:
                score2 = st.number_input(
                    f"Goals {team2}",
                    min_value=0,
                    max_value=20,
                    key=f"score2_{idx}"
                )

        pred = st.session_state.predictions.get(idx)

        if pred:
            st.success(f"Gekozen: {pred}")

        st.divider()

    if st.button("💾 Concept opslaan"):
        st.success("Concept opgeslagen.")

    if st.button("🔒 Definitief indienen"):
        st.success("Pronostiek definitief ingediend.")
