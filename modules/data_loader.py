import pandas as pd
import streamlit as st
import sys
import os

# Zorg dat de 'modules' map in het zoekpad van Python staat
current_dir = os.path.dirname(__file__)
if current_dir not in sys.path:
    sys.path.append(current_dir)

def get_matches():
    """
    Laadt de 72 wedstrijden in vanuit pronostiek_matches.py
    """
    try:
        # We proberen de import voor jouw specifieke bestandsnaam
        from pronostiek_matches import HARDCODED_MATCHES
    except (ImportError, ModuleNotFoundError):
        try:
            # Fallback voor verschillende map-structuren op Streamlit Cloud
            from modules.pronostiek_matches import HARDCODED_MATCHES
        except:
            st.error("Bestand 'pronostiek_matches.py' niet gevonden in de modules map!")
            return pd.DataFrame()

    # Maak de DataFrame
    df = pd.DataFrame(HARDCODED_MATCHES)
    
    # Forceer de types zodat sorteren en filteren goed gaat op nummer
    df['match_id'] = pd.to_numeric(df['match_id'], errors='coerce')
    df['speeldag'] = pd.to_numeric(df['speeldag'], errors='coerce')
    
    return df.sort_values('match_id')

def get_speeldagen():
    """Geeft een lijst van speeldagen (bijv. [1, 2, 3]) voor de UI slider."""
    df = get_matches()
    if df.empty:
        return [1]
    return sorted(df['speeldag'].unique().tolist())
