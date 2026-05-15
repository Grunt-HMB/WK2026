import streamlit as st


def show_pronostiek_scores(user_id=None):

    st.title("Pronostiek Scores")

    html = """
    <div style="
        display:flex;
        flex-direction:row;
        align-items:center;
        justify-content:center;
        gap:6px;
        width:100%;
        flex-wrap:nowrap;
    ">

        <div style="
            background:#1f77b4;
            color:white;
            padding:8px 14px;
            border-radius:8px;
            min-width:90px;
            text-align:center;
            font-weight:700;
            font-size:14px;
            white-space:nowrap;
        ">
            Label 1
        </div>

        <div style="
            font-size:18px;
            font-weight:700;
            white-space:nowrap;
        ">
            -*-
        </div>

        <div style="
            background:#2ca02c;
            color:white;
            padding:8px 14px;
            border-radius:8px;
            min-width:90px;
            text-align:center;
            font-weight:700;
            font-size:14px;
            white-space:nowrap;
        ">
            Label 2
        </div>

    </div>
    """

    st.markdown(html, unsafe_allow_html=True)
