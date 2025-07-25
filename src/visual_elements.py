import streamlit as st
import pandas as pd
import src.data_funcs as data_funcs
from cfg.table_schema import Cols
from streamlit.delta_generator import DeltaGenerator


def person_card(id: int, conn: DeltaGenerator):
    """Display a card with person's details."""
    # conn = st.container(border=False)
    name = data_funcs.get_col_value(id, Cols.NAME)
    birthplace = data_funcs.get_col_value(id, Cols.BIRTHPLACE)
    birthday = data_funcs.get_col_value(id, Cols.BIRTHDAY)
    deathday = data_funcs.get_col_value(id, Cols.DEATHDATE)
    relationship = data_funcs.get_relationship(
        st.session_state.get("relationship_base_id", 0), id
    )
    if relationship:
        conn.markdown(
            f"**{data_funcs.get_relationship(st.session_state.get("relationship_base_id", 0), id)}**"
        )
    conn.markdown(f"**Name**\n\n{name}")
    years = ""
    if birthday is not None:
        years = f"({birthday}"
        if deathday is not None:
            years += f" - {deathday})"
        else:
            years += ")"
    if years:
        conn.markdown(years)
    if birthplace is not None:
        conn.markdown(f"**Birthplace**\n\n{birthplace}")
    else:
        conn.markdown("**Birthplace**\n\nUnknown")
    return conn


def main_row_card(id: int) -> None:
    """Display the card for the main person, including button for parent"""
    conn = st.container(border=True)
    parent_id = data_funcs.get_col_value(id, Cols.PARENT)
    name = data_funcs.get_col_value(id, Cols.NAME)
    if parent_id is not None:
        parent_id = int(parent_id)

    if parent_id is not None:
        if conn.button(
            "See Parent(s)",
            key="parents_button",
            use_container_width=True,
            type="primary",
        ):
            st.session_state["id"] = parent_id
            st.rerun()
    person_card(id, conn)
    if id != 0:
        if conn.button(
            f"Edit {name}",
            key=f"edit_{id}",
            use_container_width=True,
            type="secondary",
        ):
            st.session_state.update(
                {"editing_id": id, "add_child": None, "add_spouse": None}
            )
            st.switch_page("pages/1_Add_person.py")


def spouse_card(id: int) -> None:
    """Display details for the souse"""
    conn = st.container(border=True)
    person_card(id, conn)
    marriage_date = data_funcs.get_col_value(id, Cols.MARRIAGEDATE)
    name = data_funcs.get_col_value(id, Cols.NAME)
    if marriage_date is not None:
        conn.markdown(f"**Marrriage Date**\n\n{marriage_date}")
    if conn.button(
        f"Edit {name}",
        key=f"edit_{id}",
        use_container_width=True,
        on_click=lambda: st.session_state.update(
            {"editing_id": id, "add_child": None, "add_spouse": None}
        ),
        type="secondary",
    ):
        st.session_state.update(
            {"editing_id": id, "add_child": None, "add_spouse": None}
        )
        st.switch_page("pages/1_Add_person.py")


def child_card(id: int) -> None:
    """Display details for a child, along with a button to show their children"""
    conn = st.container(border=True)
    person_card(id, conn)
    name = data_funcs.get_col_value(id, Cols.NAME)

    def children_button_callback():
        """Callback for the children button."""
        st.session_state["id"] = id
        st.rerun()

    conn.button(
        f"See {name} Details",
        key=f"children_button_{id}",
        on_click=children_button_callback,
        use_container_width=True,
        type="primary",
    )


def main_row(id) -> None:
    columns = st.columns(4)
    sp = data_funcs.find_spouse(id)
    with columns[0]:
        main_row_card(st.session_state["id"])
    with columns[1]:
        if sp is not None:
            if len(sp) == 1:
                st.markdown("### Spouse:")
            else:
                st.markdown("### Spouses:")
        if st.button("Add Spouse", key="add_spouse_button", type="secondary"):
            st.session_state.update(
                {"editing_id": None, "add_child": None, "add_spouse": id}
            )
            st.switch_page("pages/1_Add_person.py")
    if sp is not None:
        ids = sp.index.tolist()
        for i, id in enumerate(ids):
            col = 2 + (i % 2)
            with columns[col]:
                spouse_card(int(id))


def children_row(id) -> None:
    """Display children of a person."""
    children = data_funcs.find_children(id)
    columns = st.columns(4)
    if children is not None:
        ids = children.index.tolist()
        for i, id in enumerate(ids):
            col = i % 4
            with columns[col]:
                child_card(int(id))
