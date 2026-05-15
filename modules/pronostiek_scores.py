# Vervang je oude set_score door deze twee specifieke callback functies
    def update_score_callback(match_id, team_num, delta):
        match_id = str(match_id)
        ensure_match_prediction(match_id)
        
        current_data = st.session_state.score_predictions[match_id]
        field = f"score{team_num}"
        
        # Bereken nieuwe score
        new_val = max(0, min(int(current_data[field]) + delta, 50))
        current_data[field] = new_val
        
        # Update ook de "1-X-2" voorspelling direct
        current_data["prediction"] = result_from_score(current_data["score1"], current_data["score2"])
