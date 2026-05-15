import streamlit as st


def show_pronostiek_scores():

    st.title("Pronostiek Scores")

    st.divider()

    st.subheader("Label voorbeeld")

    col1, col2 = st.columns(2)

    with col1:
        st.info("Dit is label 1")

    with col2:
        st.success("Dit is label 2")

    st.divider()

    st.subheader("Andere voorbeelden")

    st.text("Gewone tekst label")
    st.write("Label via st.write()")

    st.markdown(
        """
        <div style="
            padding:12px;
            border-radius:10px;
            background-color:#1f2937;
            color:white;
            margin-bottom:10px;
        ">
            Custom label 1
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div style="
            padding:12px;
            border-radius:10px;
            background-color:#065f46;
            color:white;
        ">
            Custom label 2
        </div>
        """,
        unsafe_allow_html=True
    )
