import pandas as pd
import streamlit as st
import sys
import os

# Zorg dat de modules map vindbaar is voor Python
current_dir = os.path.dirname(__file__)
if current_dir not in sys.path:
    sys.path.append(current_dir)

def get_matches():
    try:
        # Importeer jouw specifieke bestand
        from pronostiek_matches import HARDCODED_MATCHES
    except (ImportError, ModuleNotFoundError):
        try:
            from modules.pronostiek_matches import HARDCODED_MATCHES
        except:
            st.error("Bestand 'pronostiek_matches.py' niet gevonden!")
            return pd.DataFrame()

    # Maak de tabel
    df = pd.DataFrame(HARDCODED_MATCHES)
    
    # Forceer alles naar het juiste type (nummers voor id's)
    df['match_id'] = pd.to_numeric(df['match_id'], errors='coerce')
    df['speeldag'] = pd.to_numeric(df['speeldag'], errors='coerce')
    
    return df.sort_values('match_id')
