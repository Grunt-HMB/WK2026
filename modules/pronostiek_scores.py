import streamlit as st

def show_pronostiek_compact():
    st.title("Pronostiek Invoer")

    # De CSS die alles geforceerd naast elkaar houdt
    st.markdown("""
    <style>
        /* Container die NOOIT onder elkaar gaat (flex-wrap: nowrap) */
        .mobile-row {
            display: flex;
            flex-direction: row;
            align-items: center;
            justify-content: flex-start;
            gap: 5px;
            width: 100%;
            overflow-x: auto; /* Zorgt dat het niet buiten beeld loopt op hele kleine schermen */
            padding: 10px 0;
        }

        .label-box {
            color: white;
            padding: 8px 6px;
            border-radius: 6px;
            font-weight: 700;
            font-size: 12px;
            text-align: center;
            flex: 1; /* Zorgt dat labels even breed zijn */
            min-width: 60px;
            white-space: nowrap;
        }

        .blue { background: #1f77b4; }
        .gray { background: #6c757d; }
        .green { background: #2ca02c; }

        /* Styling voor het invoerveld binnen de rij */
        .score-input {
            width: 80px;
            padding: 6px;
            border-radius: 6px;
            border: 1px solid #ccc;
            font-weight: bold;
            text-align: center;
        }
    </style>
    """, unsafe_allow_html=True)

    # De HTML structuur
    # Let op: De input is hier een standaard HTML input voor de look
    html_display = """
    <div class="mobile-row">
        <div class="label-box blue">Label 1</div>
        <div class="label-box gray">Label 2</div>
        <div class="label-box green">Label 3</div>
        <input type="text" class="score-input" placeholder="0 - 0">
    </div>
    """
    
    st.markdown(html_display, unsafe_allow_html=True)
    
    # Als je de waarde ECHT in Streamlit/Python wilt gebruiken:
    # Gebruik dan toch st.columns maar met de parameter 'gap' en een trucje:
    st.write("---")
    st.caption("Interactieve versie (gebruik deze voor data):")
    
    # Streamlit hack om kolommen naast elkaar te dwingen op mobiel
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1.5])
    with col1: st.markdown('<div class="label-box blue" style="min-width:auto;">L1</div>', unsafe_allow_html=True)
    with col2: st.markdown('<div class="label-box gray" style="min-width:auto;">L2</div>', unsafe_allow_html=True)
    with col3: st.markdown('<div class="label-box green" style="min-width:auto;">L3</div>', unsafe_allow_html=True)
    with col4: score = st.text_input("", key="m_score", label_visibility="collapsed")

show_pronostiek_compact()
