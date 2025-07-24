import streamlit as st
from cfg.table_schema import Cols
from src.data import Data
import src.data_funcs as data_funcs


def name(name: str, relationship: str, generation: int = 1, highlight=False) -> str:
    """A name with a unicode character prefix"""
    return (
        f"\u251c\u2500 {generation}. {name} ({relationship})"
        if not highlight
        else f"\u251c\u2500 {generation}. :green[{name}] ({relationship})"
    )


def tab(tabs: int = 1) -> str:
    return "\u2502\u2002" * tabs


def new_line() -> str:
    """A new line with a tab"""
    return "\n\n"


def person_and_children(data: Data, id: int, tabs: int = 1) -> str:
    """Write a line for the provided person, and then one for each child"""
    data = st.session_state.get("data", Data())
    person = data.id_to_person_map[id]
    highlight_list = data_funcs.get_lineage(st.session_state["relationship_base_id"])
    relationship = data_funcs.get_relationship(
        st.session_state["relationship_base_id"], id
    )
    s = name(person, relationship, generation=tabs, highlight=id in highlight_list)
    spouses = data_funcs.find_spouse(id)
    if spouses is not None:
        spouse_ids = spouses[Cols.ID].tolist()
        for s_id in spouse_ids:
            spouse_name = data.id_to_person_map[s_id]
            marriage_date = spouses[spouses[Cols.ID] == s_id][Cols.MARRIAGEDATE].values[
                0
            ]
            s += new_line() + tab(tabs) + f" x {spouse_name}"
            if marriage_date is not None:
                s += f" (x {marriage_date})"
    children = data_funcs.find_children(id)
    if children is None:
        return s
    children_ids = children[Cols.ID].tolist()
    for child_id in children_ids:
        s += new_line() + tab(tabs) + person_and_children(data, child_id, tabs=tabs + 1)

    return s


data = st.session_state.get("data", Data())
if st.button(
    "Go Back to Tree Navigation", key="return_to_tree_navigation", type="primary"
):
    st.switch_page("app.py")
st.markdown("---")
st.selectbox(
    "Select Person",
    options=data.people(),
    key="id_selectbox",
    index=data.person_index(st.session_state["id"]),
)
left, middle, right = st.columns(3)
if left.button("Set as Base", use_container_width=True, type="primary"):
    st.session_state["tree_base_id"] = data.person_to_id_map[
        st.session_state["id_selectbox"]
    ]
if middle.button("Highlight Lineage", use_container_width=True, type="primary"):
    st.session_state["relationship_base_id"] = data.person_to_id_map[
        st.session_state["id_selectbox"]
    ]
if right.button("Reset", use_container_width=True, type="primary"):
    st.session_state["tree_base_id"] = 0
    st.session_state["relationship_base_id"] = 0
base = data_funcs.get_col_value(st.session_state.get("tree_base_id", 0), Cols.NAME)
highlight = data_funcs.get_col_value(
    st.session_state.get("relationship_base_id", 0), Cols.NAME
)
st.info(
    f"We are showing the tree starting from {base}.\n\nThe relationships to {highlight} are shown, and their lineage is highlighted."
)
st.markdown("---")
st.markdown("# Full Tree")
tree_base = st.session_state.get("tree_base_id", 0)
st.markdown(person_and_children(data, tree_base))
