import streamlit as st


def ensure_prediction_state():
    if "local_predictions" not in st.session_state:
        st.session_state["local_predictions"] = {}

    if "predictions_dirty" not in st.session_state:
        st.session_state["predictions_dirty"] = False


def load_existing_predictions(user_id, predictions_df):
    ensure_prediction_state()

    loaded_key = f"loaded_predictions_{user_id}"

    if loaded_key in st.session_state:
        return

    if predictions_df is None or predictions_df.empty:
        st.session_state[loaded_key] = True
        return

    predictions = predictions_df.copy()
    predictions.columns = predictions.columns.astype(str).str.strip().str.lower()

    if "user_id" not in predictions.columns or "match_id" not in predictions.columns:
        st.session_state[loaded_key] = True
        return

    user_preds = predictions[
        predictions["user_id"].astype(str).str.strip() == str(user_id).strip()
    ]

    for _, row in user_preds.iterrows():
        match_id = str(row.get("match_id", "")).strip()

        if match_id == "":
            continue

        st.session_state["local_predictions"][match_id] = {
            "prediction": str(row.get("prediction", "")).upper().strip(),
            "score1": row.get("score1", ""),
            "score2": row.get("score2", ""),
            "status": row.get("status", ""),
        }

    st.session_state[loaded_key] = True
    st.session_state["predictions_dirty"] = False


def set_prediction(match_id, prediction):
    ensure_prediction_state()

    match_id = str(match_id).strip()
    prediction = str(prediction).upper().strip()

    current = st.session_state["local_predictions"].get(match_id, {})

    old_prediction = str(current.get("prediction", "")).upper().strip()

    current["prediction"] = prediction

    if "score1" not in current:
        current["score1"] = ""

    if "score2" not in current:
        current["score2"] = ""

    st.session_state["local_predictions"][match_id] = current

    if old_prediction != prediction:
        st.session_state["predictions_dirty"] = True


def set_score_prediction(match_id, score1, score2):
    ensure_prediction_state()

    match_id = str(match_id).strip()

    current = st.session_state["local_predictions"].get(match_id, {})

    old_score1 = str(current.get("score1", "")).strip()
    old_score2 = str(current.get("score2", "")).strip()

    current["score1"] = score1
    current["score2"] = score2

    if "prediction" not in current:
        current["prediction"] = ""

    st.session_state["local_predictions"][match_id] = current

    if old_score1 != str(score1).strip() or old_score2 != str(score2).strip():
        st.session_state["predictions_dirty"] = True


def mark_predictions_saved():
    st.session_state["predictions_dirty"] = False
