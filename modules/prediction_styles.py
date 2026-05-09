import streamlit as st


def inject_prediction_css():
    st.markdown(
        """
<style>
.phase-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-bottom: 1rem;
}

.phase-grid div[data-testid="stButton"] {
    width: auto !important;
}

.phase-grid button {
    width: auto !important;
    min-width: 42px !important;
    padding: 0.35rem 0.55rem !important;
    white-space: nowrap !important;
}

.match-actions div[data-testid="stButton"] button {
    min-width: 42px !important;
    height: 38px !important;
    padding: 0.35rem 0.45rem !important;
    white-space: nowrap !important;
}

.match-actions .score-button div[data-testid="stButton"] button {
    min-width: 72px !important;
}

@media (max-width: 700px) {
    .phase-grid {
        display: grid;
        grid-template-columns: repeat(9, minmax(34px, auto));
        gap: 5px;
    }

    .phase-grid button {
        min-width: 34px !important;
        padding: 0.3rem 0.45rem !important;
        font-size: 0.78rem !important;
    }

    .match-actions {
        margin-top: 8px;
    }
}
</style>
""",
        unsafe_allow_html=True,
    )
