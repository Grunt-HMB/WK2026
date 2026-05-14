import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager

from modules.database import append_row, get_next_user_id
from modules.utils import tournament_locked


def create_cookie_manager():
    return EncryptedCookieManager(
        prefix="wk2026_prono_",
        password=st.secrets["COOKIE_PASSWORD"],
    )


def ensure_user_columns(users_df):
    users_df = users_df.copy()

    for col in ["user_id", "naam", "pincode", "admin", "team_name"]:
        if col not in users_df.columns:
            users_df[col] = ""

    users_df["admin"] = (
        users_df["admin"]
        .astype(str)
        .str.upper()
        .isin(["TRUE", "WAAR", "1", "YES"])
    )

    return users_df


def login_user(users_df, username, password):
    users_df = ensure_user_columns(users_df)

    username = str(username or "").strip()
    password = str(password or "").strip()

    if users_df.empty:
        return None

    user = users_df[
        (users_df["naam"].astype(str).str.lower() == username.lower())
        & (users_df["pincode"].astype(str) == password)
    ]

    if user.empty:
        return None

    return user.iloc[0].to_dict()


def find_user_by_id(users_df, user_id):
    users_df = ensure_user_columns(users_df)

    if users_df.empty:
        return None

    user = users_df[
        users_df["user_id"].astype(str) == str(user_id)
    ]

    if user.empty:
        return None

    return user.iloc[0].to_dict()


def get_display_team_name(user):
    team_name = str(user.get("team_name", "") or "").strip()
    naam = str(user.get("naam", "") or "").strip()

    if team_name:
        return team_name

    return naam


def register_user(users_df, username, password, team_name):
    users_df = ensure_user_columns(users_df)

    username = str(username or "").strip()
    password = str(password or "").strip()
    team_name = str(team_name or "").strip()

    if tournament_locked():
        return False, "Registreren is afgesloten."

    if len(username) < 3:
        return False, "Naam moet minstens 3 tekens hebben."

    if len(password) < 3:
        return False, "Pincode moet minstens 3 tekens hebben."

    if len(team_name) < 3:
        return False, "Ploegnaam moet minstens 3 tekens hebben."

    existing_name = users_df[
        users_df["naam"].astype(str).str.lower() == username.lower()
    ]

    if not existing_name.empty:
        return False, "Deze naam bestaat al."

    existing_team = users_df[
        users_df["team_name"].astype(str).str.lower() == team_name.lower()
    ]

    if not existing_team.empty:
        return False, "Deze ploegnaam bestaat al."

    new_id = get_next_user_id(users_df)

    append_row(
        "Users",
        [
            new_id,
            username,
            password,
            "FALSE",
            team_name,
        ],
    )

    st.cache_data.clear()

    return True, "Account aangemaakt. Je kan nu inloggen."


def restore_login_from_cookie(users_df):
    users_df = ensure_user_columns(users_df)

    cookies = create_cookie_manager()

    if not cookies.ready():
        st.info("Cookies laden...")
        st.stop()

    if "user" not in st.session_state:
        remembered_user_id = cookies.get("user_id")

        if remembered_user_id:
            remembered_user = find_user_by_id(users_df, remembered_user_id)

            if remembered_user is not None:
                st.session_state["user"] = remembered_user

    return cookies


def logout(cookies):
    if "user" in st.session_state:
        del st.session_state["user"]

    if "user_id" in cookies:
        del cookies["user_id"]
        cookies.save()

    st.session_state.main_page = "🏠 Hoofdmenu"
    st.rerun()


def show_login_page(users_df):
    users_df = ensure_user_columns(users_df)
    cookies = create_cookie_manager()

    if not cookies.ready():
        st.info("Cookies laden...")
        st.stop()

    st.subheader("🔐 Inloggen")

    name = st.text_input("Naam", key="login_name")
    pincode = st.text_input("Pincode", type="password", key="login_pin")

    remember_me = st.checkbox(
        "Ingelogd blijven",
        value=True,
        key="remember_me",
    )

    if st.button("Inloggen", use_container_width=True, type="primary"):
        user = login_user(users_df, name, pincode)

        if user is None:
            st.error("Naam of pincode is fout.")
        else:
            st.session_state["user"] = user

            if remember_me:
                cookies["user_id"] = str(user["user_id"])
                cookies.save()

            st.session_state.main_page = "🏠 Hoofdmenu"
            st.rerun()


def show_register_page(users_df):
    users_df = ensure_user_columns(users_df)

    st.subheader("📝 Registreren")

    locked = tournament_locked()

    if locked:
        st.warning("Registreren is afgesloten.")

    name = st.text_input(
        "Nieuwe naam",
        key="reg_name",
        disabled=locked,
    )

    team_name = st.text_input(
        "Ploegnaam",
        key="reg_team_name",
        disabled=locked,
        placeholder="bv. FC Tiki Taka",
    )

    pincode = st.text_input(
        "Nieuwe pincode",
        type="password",
        key="reg_pin",
        disabled=locked,
    )

    if st.button(
        "Registreren",
        use_container_width=True,
        type="primary",
        disabled=locked,
    ):
        success, msg = register_user(users_df, name, pincode, team_name)

        if success:
            st.success(msg)
            st.info("Ga nu naar Inloggen.")
        else:
            st.error(msg)


def require_login():
    if "user" not in st.session_state:
        st.warning("Log eerst in om verder te gaan.")

        if st.button("🔐 Naar inloggen", use_container_width=True):
            st.session_state.main_page = "🔐 Inloggen"
            st.rerun()

        return None

    return st.session_state["user"]
