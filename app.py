# =========================================================
# WEDSTRIJDEN LIJST (GEFIXTE VERSIE)
# =========================================================

if st.session_state.menu_keuze == "⚽ Wedstr.":
    df = matches_df.copy()
    
    for _, match in df.iterrows():
        mid = str(match.get("match_id", ""))
        key = f"pred_{mid}"
        
        # Haal de waarde op en maak deze schoon
        raw_val = st.session_state.local_predictions.get(mid, "X")
        clean_val = str(raw_val).strip().upper()
        
        # Validatie: alleen "1", "X", of "2" zijn toegestaan als default
        # Als de waarde uit de DB corrupt is, zetten we hem op None om crashes te voorkomen
        safe_default = clean_val if clean_val in ["1", "X", "2"] else None
        
        with st.container(key=f"match_card_{mid}"):
            col_info, col_pred = st.columns([1.8, 1.0], gap="small")
            
            with col_info:
                # Datum en tijd formatie
                datum_raw = str(match.get('datum', ''))
                datum = datum_raw[5:].replace('-', '/') if len(datum_raw) > 5 else datum_raw
                tijd = str(match.get('tijd', ''))[:5]
                
                t1 = f"{country_flag(match.get('team1_code'))} {match.get('team1')}"
                t2 = f"{country_flag(match.get('team2_code'))} {match.get('team2')}"
                
                st.markdown(f"""
                <div class="match-info-container">
                    <div class="match-date"><b>{datum}</b><br>{tijd}</div>
                    <div class="match-teams">{t1}<br>{t2}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_pred:
                # Gebruik safe_default om de StreamlitAPIException te voorkomen
                st.segmented_control(
                    "P", 
                    options=["1", "X", "2"],
                    key=key,
                    default=safe_default,
                    label_visibility="collapsed"
                )