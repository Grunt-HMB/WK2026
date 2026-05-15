import pandas as pd
import streamlit as st
import sys
import os

# Voeg de huidige map toe aan het pad voor Streamlit Cloud
current_dir = os.path.dirname(__file__)
if current_dir not in sys.path:
    sys.path.append(current_dir)

def get_matches():
    try:
        # Importeer specifiek jouw bestand
        from pronostiek_matches import HARDCODED_MATCHES
    except (ImportError, ModuleNotFoundError):
        try:
            from modules.pronostiek_matches import HARDCODED_MATCHES
        except:
            st.error("Kan 'pronostiek_matches.py' niet vinden!")
            return pd.DataFrame()

    df = pd.DataFrame(HARDCODED_MATCHES)
    
    # Zet id's om naar nummers voor een strakke volgorde (1-72)
    df['match_id'] = pd.to_numeric(df['match_id'], errors='coerce')
    df['speeldag'] = pd.to_numeric(df['speeldag'], errors='coerce')
    
    return df.sort_values('match_id')
