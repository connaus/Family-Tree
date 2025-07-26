import streamlit as st
from cfg.table_schema import Cols
from src.data import Data
import src.data_funcs as data_funcs
from src.authentication import Authenticator

from src.mermaid import Mermaid, Orientation

st.set_page_config(layout="wide")
if "authenticator" not in st.session_state:
    st.session_state["authenticator"] = Authenticator()
authenticator: Authenticator = st.session_state.get("authenticator", Authenticator())
authenticator.check_login()
authenticator.authenticator.logout("Logout", "main")


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


def full_tree_list(data: Data, id: int, tabs: int = 1) -> str:
    """Write a line for the provided person, and then one for each child"""
    person = data.id_to_person_map[id]
    relationship_base_id = st.session_state.get("relationship_base_id", 0)
    highlight_list = data_funcs.get_lineage(relationship_base_id)
    relationship = data_funcs.get_relationship(relationship_base_id, id)
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
        s += new_line() + tab(tabs) + full_tree_list(data, child_id, tabs=tabs + 1)

    return s


def build_tree(
    graph: Mermaid,
    id: int,
    max_generation: int | None = None,
    include_spouses: bool = True,
    _iter: int = 1,
) -> Mermaid:
    """Write a line for the provided person, and then one for each child"""
    data: Data = st.session_state.get("data", Data())
    person = data.id_to_person_map[id]
    relationship_base_id = st.session_state.get("relationship_base_id", 0)
    highlight_list = data_funcs.get_lineage(relationship_base_id)
    relationship = data_funcs.get_relationship(relationship_base_id, id)
    graph.add_node(
        person, label=f"{person}\n{relationship}", ancestor=id in highlight_list
    )
    if include_spouses:
        spouses = data_funcs.find_spouse(id)
        if spouses is not None:
            spouse_ids = spouses[Cols.ID].tolist()
            for s_id in spouse_ids:
                spouse_name = data.id_to_person_map[s_id]
                marriage_date = spouses[spouses[Cols.ID] == s_id][
                    Cols.MARRIAGEDATE
                ].values[0]
                label = (
                    spouse_name
                    if marriage_date is None
                    else f"{spouse_name} ({marriage_date})"
                )
                graph.add_node(spouse_name, label)
                graph.add_edge(person, spouse_name, spouse=True)
    children = data_funcs.find_children(id)
    if children is None:
        return graph
    # _iter += 1
    if max_generation is not None and _iter > max_generation:
        return graph
    children_ids = children[Cols.ID].tolist()
    for child_id in children_ids:
        build_tree(
            graph,
            child_id,
            max_generation=max_generation,
            include_spouses=include_spouses,
            _iter=_iter,
        )
        child_name = data.id_to_person_map[child_id]
        graph.add_edge(person, child_name)
    return graph


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
    index=None,
    # index=data.person_index(st.session_state["id"]),
)
left, middle, right = st.columns(3)
if left.button("Set as Base", use_container_width=True, type="primary"):
    selected_id: str = (
        st.session_state.get("id_selectbox", None)
        if (isinstance(st.session_state.get("id_selectbox"), str))
        and (st.session_state.get("id_selectbox") is not None)
        else data.id_to_person_map[0]
    )
    st.session_state["tree_base_id"] = data.person_to_id_map[selected_id]
if middle.button("Highlight Lineage", use_container_width=True, type="primary"):
    selected_id: str = (
        st.session_state.get("id_selectbox", None)
        if (isinstance(st.session_state.get("id_selectbox"), str))
        and (st.session_state.get("id_selectbox") is not None)
        else data.id_to_person_map[0]
    )

    st.session_state["relationship_base_id"] = data.person_to_id_map[selected_id]
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
graph_type = st.radio("Select Graph Type", options=["Graph", "List"], horizontal=True)
tree_base = st.session_state.get("tree_base_id", 0)
if graph_type == "List":
    st.markdown(full_tree_list(data, tree_base))

else:
    max_generations = st.slider("Number of Generations to show", 1, 10, 7)
    include_spouses = st.checkbox("Include Spouses")
    st.markdown("---")
    # Create a graphlib graph object
    m = build_tree(
        Mermaid(orientation=Orientation.LR),
        id=tree_base,
        max_generation=max_generations,
        include_spouses=include_spouses,
    )
    m()
