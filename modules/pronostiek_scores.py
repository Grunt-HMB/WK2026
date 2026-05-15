import streamlit as st

def show_pronostiek_scores(label1="Team A", label2="Team B", score="-*-"):
    """
    Toont de scores in een horizontale flexbox layout.
    """
    st.title("Pronostiek Scores")

    # De HTML/CSS voor de weergave
    html = f"""
    <div style="
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: center;
        gap: 10px;
        width: 100%;
        margin-top: 20px;
    ">
        <!-- Linker Label -->
        <div style="
            background-color: #1f77b4;
            color: white;
            padding: 10px 20px;
            border-radius: 10px;
            min-width: 100px;
            text-align: center;
            font-weight: bold;
            font-size: 16px;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        ">
            {label1}
        </div>

        <!-- Score/Separator -->
        <div style="
            font-size: 24px;
            font-weight: 800;
            color: #333;
            padding: 0 10px;
        ">
            {score}
        </div>

        <!-- Rechter Label -->
        <div style="
            background-color: #2ca02c;
            color: white;
            padding: 10px 20px;
            border-radius: 10px;
            min-width: 100px;
            text-align: center;
            font-weight: bold;
            font-size: 16px;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        ">
            {label2}
        </div>
    </div>
    """

    # Gebruik markdown om de HTML te renderen
    st.markdown(html, unsafe_allow_html=True)

# De app uitvoeren
if __name__ == "__main__":
    # Optioneel: parameters meegeven voor dynamische inhoud
    show_pronostiek_scores("Thuisploeg", "Uitploeg", "2 - 1")
    
    # Extra informatie onder de scores
    st.info("Vul hieronder je eigen voorspelling in.")
