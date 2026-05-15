import streamlit as st

def show_pronostiek_scores(user_id=None):
    st.title("Pronostiek Scores")

    # De HTML in één compacte string zonder commentaren voorkomt render-fouten
    html = """
    <div style="display:flex;flex-direction:row;align-items:center;justify-content:center;gap:10px;width:100%;">
        <div style="background:#1f77b4;color:white;padding:8px 16px;border-radius:8px;text-align:center;font-weight:700;font-size:14px;white-space:nowrap;">
            Label 1
        </div>
        <div style="font-size:18px;font-weight:700;white-space:nowrap;color:#333;">
            -*-
        </div>
        <div style="background:#2ca02c;color:white;padding:8px 16px;border-radius:8px;text-align:center;font-weight:700;font-size:14px;white-space:nowrap;">
            Label 2
        </div>
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)

show_pronostiek_scores()
