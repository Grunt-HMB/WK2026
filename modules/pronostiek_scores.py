import streamlit as st


def show_pronostiek_scores(user_id=None):
    st.title("Pronostiek Scores")

    st.write(f"Gebruiker: {user_id}")

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info("Label 1")

    with col2:
        st.success("-----")

    with col3:
        st.success("Label 2")
