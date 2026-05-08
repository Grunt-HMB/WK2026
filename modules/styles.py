import streamlit as st

def inject_css():
    st.markdown("""
<style>
/* Algemene layout */
.block-container {
    padding-top: 1.6rem;
    padding-bottom: 2rem;
    max-width: 1240px;
}

.main-title {
    font-size: 2.25rem;
    font-weight: 800;
    margin-bottom: 0.2rem;
}

.page-subtitle {
    color: #475569;
    margin-bottom: 1.8rem;
    font-size: 1rem;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #06152d 0%, #071d3f 100%);
}

section[data-testid="stSidebar"] * {
    color: white;
}

.sidebar-card {
    border: 1px solid rgba(255,255,255,0.18);
    border-radius: 14px;
    padding: 16px;
    margin: 12px 0 18px 0;
    background: rgba(255,255,255,0.06);
}

.sidebar-name {
    color: #22c55e;
    font-size: 1.25rem;
    font-weight: 800;
}

/* Match cards */
.match-card {
    border: 1px solid #dbe2ea;
    background: #ffffff;
    border-radius: 14px;
    padding: 20px 22px;
    margin: 14px 0;
    box-shadow: 0 2px 14px rgba(15, 23, 42, 0.04);
}

.match-grid {
    display: grid;
    grid-template-columns: 150px 1fr 320px;
    gap: 24px;
    align-items: center;
}

.datebox {
    color: #0f172a;
    font-size: 0.95rem;
    line-height: 1.85;
    min-width: 120px;
}

.teams {
    display: grid;
    grid-template-columns: 1fr 22px 1fr;
    gap: 16px;
    align-items: center;
}

.team {
    display: flex;
    align-items: center;
    gap: 14px;
    min-width: 0;
}

.team.right {
    justify-content: flex-start;
}

.flag {
    font-size: 3rem;
    line-height: 1;
    filter: drop-shadow(0 2px 3px rgba(0,0,0,0.12));
}

.team-name {
    font-size: 1.15rem;
    font-weight: 800;
    color: #0f172a;
    white-space: nowrap;
}

.team-code {
    color: #334155;
    font-size: 0.92rem;
    font-weight: 600;
}

.vs {
    font-weight: 800;
    color: #111827;
    text-align: center;
}

.choice-row {
    display: flex;
    gap: 10px;
    justify-content: flex-end;
    align-items: center;
}

.choice-label {
    font-size: 0.85rem;
    color: #475569;
    text-align: right;
    margin-top: 8px;
}

/* Streamlit buttons */
div[data-testid="stButton"] > button {
    border-radius: 10px;
    min-height: 46px;
    font-weight: 800;
    border: 1px solid #d6dde8;
}

.btnbar div[data-testid="column"] {
    padding: 0 !important;
}

/* Info boxes */
.info-box {
    border: 1px solid #bfdbfe;
    background: #eff6ff;
    color: #1e3a8a;
    padding: 18px 22px;
    border-radius: 14px;
    margin-top: 20px;
}

.footer-line {
    border-top: 1px solid #e2e8f0;
    margin-top: 40px;
    padding-top: 16px;
    text-align: center;
    color: #64748b;
}

/* Mobiel */
@media (max-width: 800px) {
    .block-container {
        padding-left: 0.7rem;
        padding-right: 0.7rem;
        padding-top: 0.7rem;
    }

    .main-title {
        font-size: 1.55rem;
    }

    .match-card {
        padding: 14px;
        margin: 10px 0;
    }

    .match-grid {
        grid-template-columns: 1fr;
        gap: 12px;
    }

    .teams {
        grid-template-columns: 1fr 18px 1fr;
        gap: 8px;
    }

    .team {
        gap: 8px;
    }

    .flag {
        font-size: 2.15rem;
    }

    .team-name {
        font-size: 1rem;
        white-space: normal;
    }

    .choice-row {
        justify-content: stretch;
    }
}
</style>
""", unsafe_allow_html=True)
