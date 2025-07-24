import streamlit as st
from cfg.table_schema import Cols
from src import data_funcs
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
st.session_state["relationship_base_id"] = st.session_state.get(
    "relationship_base_id", 0
)
st.session_state["edit_row"] = None
st.session_state["add_child"] = None
st.session_state["add_spouse"] = None

data: Data = st.session_state.get("data", Data())

st.markdown("# Tree Navigation")
st.warning(
    "This site shows the descendants of Patrick and Owen Connaughton. Only their direct descendants and their spouses are included."
)
st.markdown("---")
st.markdown("## Options")
st.info(
    "This page shows a specific decendant along with their children and spouse(s).\n\nTo see the full tree click here:"
)
if st.button("View Full Tree", key="full_tree_navigation", type="primary"):
    st.switch_page("pages/Full_Tree.py")
st.write(" ")
st.write(" ")
st.selectbox(
    "Select Person",
    options=data.people(),
    key="id_selectbox",
    index=None,
)
left, right = st.columns(2)
if left.button(
    "Switch to This Person",
    key="switch_button",
    use_container_width=True,
    type="primary",
):
    selected_id: str = (
        st.session_state.get("id_selectbox", None)
        if (isinstance(st.session_state.get("id_selectbox"), str))
        and (st.session_state.get("id_selectbox") is not None)
        else data.id_to_person_map[0]
    )
    st.session_state["id"] = data.person_to_id_map[selected_id]
if right.button(
    "Show Relationships to this Person",
    key="relationship_button",
    use_container_width=True,
    type="primary",
):
    st.session_state["relationship_base_id"] = data.person_to_id_map[
        st.session_state["id_selectbox"]
    ]
st.info(
    f"Showing relationship to {data_funcs.get_col_value(st.session_state.relationship_base_id, Cols.NAME)}. Use the drop down menu above to change this."
)
st.markdown("---")
st.markdown("## Descendant")
lineage = data_funcs.get_lineage(st.session_state["id"])
ca = data_funcs.common_ancestors(
    st.session_state["relationship_base_id"], st.session_state["id"]
)
if lineage:
    lineage_names = [
        (
            f"**{data_funcs.get_col_value(i, Cols.NAME)}**"
            if i in ca
            else str(data_funcs.get_col_value(i, Cols.NAME))
        )
        for i in lineage
    ]
    st.markdown(f"({', '.join(lineage_names)})")
ve.main_row(st.session_state["id"])

st.markdown("""---""")
left, middle, right = st.columns([2, 1, 2])
st.markdown("## Children")
cols = st.columns(4)
with cols[0]:
    if st.button(
        "Add Child", key=f"add_child_{id}", use_container_width=True, type="secondary"
    ):
        st.session_state.update(
            {
                "editing_id": None,
                "add_child": st.session_state["id"],
                "add_spouse": None,
            }
        )
        st.switch_page("pages/1_Add_person.py")
ve.children_row(st.session_state["id"])
