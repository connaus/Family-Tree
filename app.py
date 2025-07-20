import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import streamlit_authenticator as stauth
from cfg.table_schema import Cols
import src.visual_elements as ve

st.set_page_config(layout="wide")
username = list(dict(st.secrets["credentials"]["usernames"]).keys())[
    0
]  # assumes only one user
auth_dict = {
    "usernames": {username: dict(st.secrets["credentials"]["usernames"][username])}
}
authenticator = stauth.Authenticate(
    auth_dict,
    st.secrets["cookie"]["name"],
    st.secrets["cookie"]["key"],
    st.secrets["cookie"]["expiry_days"],
)

authenticator.login()
if st.session_state["authentication_status"] is None:
    st.warning("Please enter the username and password to log in.")
    st.stop()

if not st.session_state["authentication_status"]:
    st.error("Username/password is incorrect")
    st.stop()


def read_data() -> pd.DataFrame:
    conn = st.connection("gsheets", type=GSheetsConnection)

    df = conn.read(worksheet="Sheet1", dtype={"birthday": str, "deathdate": str})
    df.set_index("id", inplace=True, drop=False)
    return df


authenticator.logout("Logout", "main")

# initialise session states
st.session_state["data"] = read_data()
st.session_state["id"] = st.session_state.get("id", 25)

ve.main_row(st.session_state["id"])

st.markdown("""---""")
left, middle, right = st.columns([2, 1, 2])
middle.markdown("Children")
ve.children_row(st.session_state["id"])
