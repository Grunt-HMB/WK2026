import pandas as pd
import streamlit as st
# Importeer de hardcoded lijst uit je andere bestand
try:
    from modules.pronostiek_matches import HARDCODED_MATCHES
except ModuleNotFoundError:
    from pronostiek_matches import HARDCODED_MATCHES

def get_matches():
    """
    Laadt de 72 wedstrijden in een DataFrame en bereidt de data voor.
    """
    # 1. Maak de DataFrame
    df = pd.DataFrame(HARDCODED_MATCHES)
    
    # 2. Data Schoonmaken & Typecasting
    # Zorg dat numerieke kolommen ook echt nummers zijn voor sortering
    df['match_id'] = pd.to_numeric(df['match_id'])
    df['speeldag'] = pd.to_numeric(df['speeldag'])
    
    # 3. Sorteren
    # We sorteren standaard op match_id zodat de volgorde logisch is
    df = df.sort_values(by='match_id')
    
    return df

def get_speeldagen():
    """Handige hulpfunctie voor je filters"""
    df = get_matches()
    return sorted(df['speeldag'].unique())

def get_groepen():
    """Handige hulpfunctie voor je filters"""
    df = get_matches()
    # Filter lege groepen eruit (voor de knock-out fase later)
    groepen = df[df['groep'] != ""]['groep'].unique()
    return sorted(groepen)
