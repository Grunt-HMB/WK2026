import streamlit as st

def show_pronostiek_scores(user_id=None):
    st.title("Pronostiek Scores")

    html = """
    <div style="
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: center;
        gap: 10px;
        width: 100%;
    ">
        <!-- Label 1: Breedte past zich aan de tekst aan -->
        <div style="
            background: #1f77b4;
            color: white;
            padding: 8px 16px;
            border-radius: 8px;
            text-align: center;
            font-weight: 700;
            font-size: 14px;
            white-space: nowrap;
        ">
            Label 1
        </div>

        <!-- Middenstuk -->
        <div style="
            font-size: 18px;
            font-weight: 700;
            white-space: nowrap;
            color: #333;
        ">
            -*-
        </div>

        <!-- Label 2: Breedte past zich aan de tekst aan -->
        <div style="
            background: #2ca02c;
            color: white;
            padding: 8px 16px;
            border-radius: 8px;
            text-align: center;
            font-weight: 700;
            font-size: 14px;
            white-space: nowrap;
        ">
            Label 2
        </div>
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)

# Vergeet niet de functie aan te roepen om resultaat te zien
show_pronostiek_scores()
