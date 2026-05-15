import streamlit as st


def show_pronostiek_scores(user_id=None):

    st.title("Pronostiek Scores")

    col1, mid, col2 = st.columns([5, 1, 5])

    with col1:
        st.info("Label 1")

    with mid:
        st.markdown(
            "<h2 style='text-align:center;'>-*-</h2>",
            unsafe_allow_html=True
        )

    with col2:
        st.success("Label 2")
