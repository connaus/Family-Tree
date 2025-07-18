import streamlit as st
import pandas as pd
import src.data_funcs as data_funcs
from cfg.table_schema import Cols


def person_card(id: int):
    """Display a card with person's details."""
    conn = st.container(border=True)
    name = data_funcs.get_col_value(id, Cols.NAME)
    birthplace = data_funcs.get_col_value(id, Cols.BIRTHPLACE)
    birthday = data_funcs.get_col_value(id, Cols.BIRTHDAY)
    deathday = data_funcs.get_col_value(id, Cols.DEATHDATE)
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


def main_row(id) -> None:
    columns = st.columns(4)
    sp = data_funcs.find_spouse(id)
    with columns[0]:
        person_card(st.session_state["id"])
    with columns[1]:
        if sp is not None:
            if len(sp) == 1:
                st.markdown("Spouse:")
            else:
                st.markdown("Spouses:")
    if sp is not None:
        ids = sp.index.tolist()
        for i, id in enumerate(ids):
            col = 2 + (i % 2)
            with columns[col]:
                person_card(int(id))


def children_row(id) -> None:
    """Display children of a person."""
    children = data_funcs.find_children(id)
    if children is None:
        return
    columns = st.columns(4)
    ids = children.index.tolist()
    for i, id in enumerate(ids):
        col = i % 4
        with columns[col]:
            person_card(int(id))
