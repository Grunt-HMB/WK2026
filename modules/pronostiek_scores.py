import streamlit as st

def show_pronostiek_scores(label1="Label 1", label2="Label 2", score="-*-"):
    st.title("Pronostiek Scores")

    # 1. Definieer de styling apart (CSS)
    # Dit houdt je HTML structuur schoon en overzichtelijk
    css = """
    <style>
        .score-container {
            display: flex;
            flex-direction: row;
            align-items: center;
            justify-content: center;
            gap: 10px;
            width: 100%;
        }
        .team-label {
            color: white;
            padding: 8px 16px;
            border-radius: 8px;
            text-align: center;
            font-weight: 700;
            font-size: 14px;
            white-space: nowrap;
        }
        .blue { background: #1f77b4; }
        .green { background: #2ca02c; }
        .score-divider {
            font-size: 18px;
            font-weight: 700;
            white-space: nowrap;
            color: #333;
        }
    </style>
    """

    # 2. De HTML structuur (nu heel kort en leesbaar)
    html = f"""
    {css}
    <div class="score-container">
        <div class="team-label blue">{label1}</div>
        <div class="score-divider">{score}</div>
        <div class="team-label green">{label2}</div>
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)

# Test de functie
show_pronostiek_scores("België", "Frankrijk", "2 - 1")
