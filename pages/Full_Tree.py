import streamlit as st
from cfg.table_schema import Cols
from src.data import Data
import src.data_funcs as data_funcs
from src.authentication import Authenticator
import graphviz

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


def full_tree_graph(
    data: Data,
    graph: graphviz.Digraph,
    id: int,
    max_generation: int | None = None,
    include_spouses: bool = True,
    _iter: int = 1,
) -> graphviz.Digraph:
    """Write a line for the provided person, and then one for each child"""
    person = data.id_to_person_map[id]
    relationship_base_id = st.session_state.get("relationship_base_id", 0)
    highlight_list = data_funcs.get_lineage(relationship_base_id)
    relationship = data_funcs.get_relationship(relationship_base_id, id)
    color = "green" if id in highlight_list else "black"
    label = str(data_funcs.get_col_value(id, Cols.NAME))
    dob = data_funcs.get_col_value(id, Cols.BIRTHDAY)
    dod = data_funcs.get_col_value(id, Cols.DEATHDATE)
    if dob and dod:
        label += f"\n({dob} - {dod})"
    elif dob:
        label += f"\n({dob})"
    elif dod:
        label += f"\n({dod})"
    label += f"\n{relationship}"
    graph.node(person, label=label, color=color)
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
                graph.node(spouse_name, label, color="blue")
                graph.edge(person, spouse_name, style="dashed", color="blue")
    children = data_funcs.find_children(id)
    if children is None:
        return graph
    _iter += 1
    if max_generation is not None and _iter > max_generation:
        return graph
    children_ids = children[Cols.ID].tolist()
    for child_id in children_ids:
        full_tree_graph(
            data,
            graph,
            child_id,
            max_generation=max_generation,
            include_spouses=include_spouses,
            _iter=_iter,
        )
        color = "green" if child_id in highlight_list else "black"
        graph.edge(person, data.id_to_person_map[child_id], color=color)
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
t1, t2 = st.tabs(["List", "Graph"])
tree_base = st.session_state.get("tree_base_id", 0)
t1.markdown(full_tree_list(data, tree_base))

max_generations = t2.slider("Number of Generations to show", 1, 10, 7)
include_spouses = t2.checkbox("Include Spouses")
t2.markdown("---")
# Create a graphlib graph object
graph = graphviz.Digraph(graph_attr={"rankdir": "LR", "fontsize": "80"})
graph = full_tree_graph(
    data,
    graph,
    id=tree_base,
    max_generation=max_generations,
    include_spouses=include_spouses,
)
# graph = graph.unflatten()
t2.graphviz_chart(graph, use_container_width=False)
