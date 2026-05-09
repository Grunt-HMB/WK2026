import copy
import streamlit as st

from modules.utils import result_from_score


def ensure_prediction_state():
    if "local_predictions" not in st.session_state:
        st.session_state["local_predictions"] = {}

    if "saved_predictions_snapshot" not in st.session_state:
        st.session_state["saved_predictions_snapshot"] = {}

    if "unsaved_changes" not in st.session_state:
        st.session_state["unsaved_changes"] = False


def mark_predictions_saved():
    ensure_prediction_state()
    st.session_state["saved_predictions_snapshot"] = copy.deepcopy(
        st.session_state["local_predictions"]
    )
    st.session_state["unsaved_changes"] = False


def discard_unsaved_predictions():
    ensure_prediction_state()
    st.session_state["local_predictions"] = copy.deepcopy(
        st.session_state["saved_predictions_snapshot"]
    )
    st.session_state["unsaved_changes"] = False


def load_existing_predictions(user_id, predictions_df):
    ensure_prediction_state()

    loaded_key = f"loaded_predictions_{user_id}"

    if loaded_key in st.session_state:
        return

    if predictions_df.empty:
        st.session_state[loaded_key] = True
        mark_predictions_saved()
        return

    user_preds = predictions_df[
        predictions_df["user_id"].astype(str) == str(user_id)
    ]

    for _, row in user_preds.iterrows():
        match_id = str(row.get("match_id", "")).strip()

        if match_id:
            st.session_state["local_predictions"][match_id] = {
                "prediction": str(row.get("prediction", "")).upper().strip(),
                "score1": "",
                "score2": "",
            }

    st.session_state[loaded_key] = True
    mark_predictions_saved()


def user_is_final(user_id, predictions_df):
    if predictions_df.empty:
        return False

    user_preds = predictions_df[
        predictions_df["user_id"].astype(str) == str(user_id)
    ]

    if user_preds.empty:
        return False

    return (user_preds["status"].astype(str).str.upper() == "FINAL").any()


def set_prediction(match_id, choice):
    ensure_prediction_state()

    st.session_state["local_predictions"][str(match_id)] = {
        "prediction": str(choice).upper().strip(),
        "score1": "",
        "score2": "",
    }

    st.session_state["unsaved_changes"] = True


def set_score(match_id, score1, score2):
    ensure_prediction_state()

    prediction = result_from_score(score1, score2)

    st.session_state["local_predictions"][str(match_id)] = {
        "prediction": prediction,
        "score1": "",
        "score2": "",
    }

    st.session_state["unsaved_changes"] = True
