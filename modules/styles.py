import streamlit as st


def inject_css():
    st.markdown(
        """
<style>
.block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
    max-width: 1180px;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #06152d 0%, #071d3f 100%);
}

section[data-testid="stSidebar"] * {
    color: white;
}

.sidebar-card {
    border: 1px solid rgba(255,255,255,0.18);
    border-radius: 14px;
    padding: 14px;
    margin: 12px 0 18px 0;
    background: rgba(255,255,255,0.06);
}

.sidebar-name {
    color: #22c55e;
    font-size: 1.2rem;
    font-weight: 800;
}

/* Compacte kaarten */
div[data-testid="stVerticalBlockBorderWrapper"] {
    padding-top: 0.45rem !important;
    padding-bottom: 0.45rem !important;
}

/* Compacte knoppen */
div[data-testid="stButton"] > button {
    min-height: 34px !important;
    height: 34px !important;
    padding: 0.15rem 0.35rem !important;
    border-radius: 8px !important;
    font-size: 0.82rem !important;
    font-weight: 800 !important;
}

/* Minder ruimte tussen kolommen */
div[data-testid="stHorizontalBlock"] {
    gap: 0.35rem !important;
}

/* Compacte tekst */
p {
    margin-bottom: 0.25rem !important;
}

/* Mobiel */
@media (max-width: 800px) {
    .block-container {
        padding-left: 0.45rem;
        padding-right: 0.45rem;
    }

    div[data-testid="stButton"] > button {
        min-height: 32px !important;
        height: 32px !important;
        font-size: 0.78rem !important;
    }
}
</style>
""",
        unsafe_allow_html=True,
    )
