import streamlit as st

def show_login():
    st.sidebar.title("Login")

    username = st.sidebar.text_input("Naam")
    password = st.sidebar.text_input("Pincode", type="password")

    if st.sidebar.button("Inloggen"):
        if username:
            st.session_state["user"] = username

    return st.session_state.get("user")
