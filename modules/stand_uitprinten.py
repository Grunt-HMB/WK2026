import streamlit as st
import streamlit.components.v1 as components


def show_stand_uitprinten():
    st.title("🖨️ Stand uitprinten")

    team1 = "Mexico"
    team2 = "Zuid-Afrika"

    html = f"""
    <div style="max-width:420px;margin:40px auto;font-family:Arial;">
        <div style="display:grid;grid-template-columns:1fr 70px 70px 1fr;gap:10px;align-items:center;">

            <div style="text-align:right;font-size:20px;font-weight:700;">
                {team1}
            </div>

            <input 
                id="score1"
                type="text"
                inputmode="numeric"
                pattern="[0-9]*"
                placeholder="0"
                style="font-size:24px;text-align:center;padding:10px;border-radius:8px;border:1px solid #ccc;width:60px;"
            >

            <input 
                id="score2"
                type="text"
                inputmode="numeric"
                pattern="[0-9]*"
                placeholder="0"
                style="font-size:24px;text-align:center;padding:10px;border-radius:8px;border:1px solid #ccc;width:60px;"
            >

            <div style="text-align:left;font-size:20px;font-weight:700;">
                {team2}
            </div>

        </div>
    </div>
    """

    components.html(html, height=220)
