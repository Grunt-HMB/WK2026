import streamlit as st

def show_pronostiek_scores(user_id="Gast", team1="Team A", team2="Team B", score="-*-"):
    """
    Toont de pronostiek scores in een nette layout.
    """
    st.title(f"Pronostiek Scores van {user_id}")

    # CSS voor een strakke weergave
    css = """
    <style>
        .score-container {
            display: flex;
            flex-direction: row;
            align-items: center;
            justify-content: center;
            gap: 12px;
            width: 100%;
            margin: 20px 0;
        }
        .team-box {
            color: white;
            padding: 10px 15px;
            border-radius: 8px;
            min-width: 100px;
            text-align: center;
            font-weight: 700;
            font-size: 14px;
            white-space: nowrap;
        }
        .blue { background: #1f77b4; }
        .green { background: #2ca02c; }
        .divider {
            font-size: 20px;
            font-weight: 800;
            color: #333;
        }
    </style>
    """

    # HTML structuur
    html = f"""
    {css}
    <div class="score-container">
        <div class="team-box blue">{team1}</div>
        <div class="divider">{score}</div>
        <div class="team-box green">{team2}</div>
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)

# --- LOGICA OM DE APP VEILIG UIT TE VOEREN ---

# Stel dat 'user' uit je login-systeem komt
# We initialiseren 'user' hier even als voorbeeld (haal dit weg als het al elders staat)
if 'user' not in locals():
    user = None 

# VEILIGHEIDSCHECK: Alleen uitvoeren als 'user' bestaat en de 'naam' bevat
if user is not None and isinstance(user, dict) and "naam" in user:
    show_pronostiek_scores(
        user_id=user["naam"], 
        team1="België", 
        team2="Nederland", 
        score="2 - 1"
    )
else:
    # Als er niemand is ingelogd, tonen we een algemene versie of een melding
    st.warning("Meld je aan om je persoonlijke scores te zien.")
    # Optioneel toch de layout tonen met standaardwaarden:
    show_pronostiek_scores(user_id="Bezoeker")
