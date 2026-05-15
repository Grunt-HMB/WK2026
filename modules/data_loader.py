import pandas as pd
import streamlit as st
import sys
import os

# Stap 1: Zorg dat Python de huidige 'modules' map kan vinden
# Dit voorkomt de ModuleNotFoundError op Streamlit Cloud
current_dir = os.path.dirname(__file__)
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Stap 2: Importeer de wedstrijden
# We proberen beide manieren van importeren voor maximale compatibiliteit
try:
    from matches import HARDCODED_MATCHES
except (ImportError, ModuleNotFoundError):
    try:
        from modules.matches import HARDCODED_MATCHES
    except (ImportError, ModuleNotFoundError):
        st.error("Fout: Kan 'matches.py' niet vinden in de modules map.")
        HARDCODED_MATCHES = []

def get_matches():
    """
    Zet de hardcoded lijst om naar een Pandas DataFrame voor makkelijk filteren.
    """
    if not HARDCODED_MATCHES:
        return pd.DataFrame()

    df = pd.DataFrame(HARDCODED_MATCHES)
    
    # Forceer numerieke types voor sortering en filtering
    df['match_id'] = pd.to_numeric(df['match_id'], errors='coerce')
    df['speeldag'] = pd.to_numeric(df['speeldag'], errors='coerce')
    
    # Sorteer op match_id
    return df.sort_values('match_id')

def get_speeldagen():
    """Geeft een lijst van unieke speeldagen terug voor je slider."""
    df = get_matches()
    if df.empty:
        return [1]
    return sorted(df['speeldag'].unique().tolist())
