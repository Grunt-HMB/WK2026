import pandas as pd
import streamlit as st
import sys
import os

# Zorg dat de modules map vindbaar is
current_dir = os.path.dirname(__file__)
if current_dir not in sys.path:
    sys.path.append(current_dir)

def get_matches():
    try:
        from pronostiek_matches import HARDCODED_MATCHES
    except (ImportError, ModuleNotFoundError):
        try:
            from modules.pronostiek_matches import HARDCODED_MATCHES
        except:
            st.error("Bestand 'pronostiek_matches.py' niet gevonden!")
            return pd.DataFrame()

    df = pd.DataFrame(HARDCODED_MATCHES)
    
    # Numerieke id's voor een logische volgorde (1 t/m 72)
    df['match_id'] = pd.to_numeric(df['match_id'], errors='coerce')
    df['speeldag'] = pd.to_numeric(df['speeldag'], errors='coerce')
    
    return df.sort_values('match_id')
