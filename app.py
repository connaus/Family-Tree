import streamlit as st
from src.data import Data
import src.visual_elements as ve
from src.authentication import Authenticator

st.set_page_config(layout="wide")

authenticator: Authenticator = st.session_state.get("authenticator", Authenticator())
authenticator.check_login()
authenticator.authenticator.logout("Logout", "main")

# initialise session states
if "data" not in st.session_state:
    st.session_state["data"] = Data()
st.session_state["id"] = st.session_state.get("id", 0)
st.session_state["edit_row"] = None
st.session_state["add_child"] = None
st.session_state["add_spouse"] = None

data: Data = st.session_state["data"]

st.markdown("# Tree Navigation")
if st.button(
    "See Full Tree",
    key="full_tree_navigation",
):
    st.switch_page("pages/Full_Tree.py")
st.selectbox(
    "Select Person",
    options=data.people,
    key="id_selectbox",
    index=data.person_index(st.session_state["id"]),
    on_change=lambda: st.session_state.update(
        {"id": data.person_to_id_map[st.session_state["id_selectbox"]]}
    ),
)
ve.main_row(st.session_state["id"])

st.markdown("""---""")
left, middle, right = st.columns([2, 1, 2])
middle.markdown("Children")
ve.children_row(st.session_state["id"])
