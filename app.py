import streamlit as st
from streamlit_gsheets import GSheetsConnection
import streamlit_authenticator as stauth

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

conn = st.connection("gsheets", type=GSheetsConnection)

df = conn.read(
    worksheet="Sheet1",
)

st.dataframe(df)
