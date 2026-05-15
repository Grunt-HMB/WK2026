import streamlit as st

def show_pronostiek_invoer():
    st.title("Pronostiek Invoer")

    # CSS om kolommen NAAST elkaar te dwingen, ook op mobiel
    st.markdown("""
        <style>
        /* Forceer kolommen om niet te stapelen op mobiel */
        [data-testid="column"] {
            width: calc(25% - 1rem) !important;
            flex: 1 1 calc(25% - 1rem) !important;
            min-width: 50px !important;
        }

        /* Styling voor de labels */
        .label-box {
            color: white;
            padding: 8px 2px;
            border-radius: 8px;
            text-align: center;
            font-weight: 700;
            font-size: 14px;
            white-space: nowrap;
            width: 100%;
            display: block;
        }
        .blue { background-color: #1f77b4; }
        .gray { background-color: #6c757d; }
        .green { background-color: #2ca02c; }
        
        /* Verberg het label boven het invoerveld */
        .stTextInput label { display: none; }
        </style>
    """, unsafe_allow_html=True)

    # Gebruik 4 kolommen
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown('<div class="label-box blue">Label 1</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="label-box gray">Label 2</div>', unsafe_allow_html=True)
        
    with col3:
        st.markdown('<div class="label-box green">Label 3</div>', unsafe_allow_html=True)

    with col4:
        # Hier wordt de score opgeslagen in Python
        score_input = st.text_input("Score", key="score_field", placeholder="0-0")

    # Toon resultaat ter bevestiging
    if score_input:
        st.success(f"Opgeslagen score: {score_input}")

# Voer de functie uit
if __name__ == "__main__":
    show_pronostiek_invoer()
