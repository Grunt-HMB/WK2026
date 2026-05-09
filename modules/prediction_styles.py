import streamlit as st


def inject_prediction_css():
    st.markdown(
        """
<style>
div[data-testid="stVerticalBlockBorderWrapper"] {
    padding-top: 0.55rem !important;
    padding-bottom: 0.55rem !important;
}

.match-row {
    display: grid;
    grid-template-columns: 110px minmax(260px, 1fr) 210px;
    align-items: center;
    gap: 14px;
    min-height: 48px;
}

.match-date {
    font-size: 0.78rem;
    font-weight: 800;
    color: #7da2d6;
    line-height: 1.25;
}

.match-teams {
    display: grid;
    grid-template-columns: minmax(110px, 1fr) 24px minmax(110px, 1fr);
    align-items: center;
    gap: 8px;
    font-size: 1rem;
    font-weight: 900;
}

.team-left,
.team-right {
    display: flex;
    align-items: center;
    gap: 8px;
    min-width: 0;
}

.team-name {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.match-score {
    color: #7da2d6;
    font-weight: 900;
    text-align: center;
}

.match-actions {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
}

.match-actions div[data-testid="stButton"] button {
    height: 36px !important;
    min-height: 36px !important;
    padding: 0.25rem 0.5rem !important;
    font-weight: 900 !important;
}

@media (max-width: 700px) {
    .match-row {
        grid-template-columns: 1fr;
        gap: 8px;
        min-height: 0;
    }

    .match-date {
        font-size: 0.72rem;
    }

    .match-teams {
        grid-template-columns: 1fr 18px 1fr;
        font-size: 0.88rem;
    }

    .match-actions {
        grid-template-columns: repeat(3, 1fr);
    }

    .match-actions div[data-testid="stButton"] button {
        height: 34px !important;
        min-height: 34px !important;
        padding: 0.2rem 0.35rem !important;
        font-size: 0.85rem !important;
    }
}
</style>
""",
        unsafe_allow_html=True,
    )
