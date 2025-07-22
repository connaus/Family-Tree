import pandas as pd
import streamlit as st

from cfg.table_schema import Cols
from src.data import Data


def get_person_details(id: int | list[int]) -> pd.DataFrame | pd.Series:
    """retreive the row of the person with the id"""
    df: pd.DataFrame = st.session_state.get("data", Data()).df
    if isinstance(id, float):
        id = int(id)
    person = df.loc[id]
    if person.empty:
        raise ValueError(f"Person with id {id} not found.")
    return person


def get_col_value(id: int, column: Cols) -> int | str | None:
    """get the detail of a person by id and column name"""
    person = get_person_details(id)
    value = person[column]
    if pd.notna(value):
        return value
    return None


def find_spouse(id: int) -> pd.DataFrame | None:
    """find the spouse of a person by id"""
    df: pd.DataFrame = st.session_state.get("data", Data()).df
    df = df[df[Cols.SPOUSE] == id]
    if df.empty:
        return None
    return df


def find_children(id: int) -> pd.DataFrame | None:
    """find the spouse of a person by id"""
    df: pd.DataFrame = st.session_state.get("data", Data()).df
    df = df[df[Cols.PARENT] == id]
    if df.empty:
        return None
    return df


@st.cache_data
def get_lineage(id) -> list[int]:
    """returns a list of ids startig with the provided id and ending with the First Male Connaughton"""
    parent = get_col_value(id, Cols.PARENT)
    if parent is None:
        return [id]
    return [id] + get_lineage(parent)


@st.cache_data
def common_ancestor(start_id: int, end_id: int) -> int:
    """returns teh id of the common ancestor between two people"""
    start_lineage = get_lineage(start_id)
    end_lineage = get_lineage(end_id)
    return int([i for i in start_lineage if i in end_lineage][0])


@st.cache_data
def get_shortest_path(start_id: int, end_id: int) -> list[int]:
    """returns a list of ids, where each subsequesnt id is a parent or child of the previous person.
    start_id will be the first id on the list and end_id will be the last id"""
    start_to_ca = [
        int(i) for i in get_lineage(start_id) if i not in get_lineage(end_id)
    ]
    end_to_ca = [int(i) for i in get_lineage(end_id) if i not in get_lineage(start_id)]
    return start_to_ca + [common_ancestor(start_id, end_id)] + end_to_ca


@st.cache_data
def get_relationship(start_id: int, end_id: int) -> str:
    """returns the relationship between the two supplied people"""
    path = get_shortest_path(start_id, end_id)
    ca = common_ancestor(start_id, end_id)
    ca_idx = path.index(ca)
    pl = len(path)
    if pl == 0:
        return "Not Direct Relation"
    if pl == 1:
        return "Self"
    if pl == 2:
        if ca_idx == 0:
            return "Child"
        elif ca_idx == 1:
            return "Parent"
        else:
            raise ValueError("There is something wrong with the relationship logic.")
    if pl == 3:
        if ca_idx == 0:
            return "Grandchild"
        elif ca_idx == 1:
            return "Sibling"
        elif ca_idx == 2:
            return "Grandparent"
        else:
            raise ValueError("There is something wrong with the relationship logic.")
    if pl == 4:
        if ca_idx == 0:
            return "Great Grandchild"
        elif ca_idx == 1:
            return "Niece/Nephew"
        elif ca_idx == 2:
            return "Uncle/Aunt"
        elif ca_idx == 3:
            return "Great Grandparent"
        else:
            raise ValueError("There is something wrong with the relationship logic.")
    if pl >= 5 and ca_idx == 0:
        return f"Great X{pl-3} Grandchild"
    if pl >= 5 and ca_idx == pl - 1:
        return f"Great X{pl-3} Grandparent"
    if pl == 5:
        if ca_idx == 1:
            return "Grand-niece/Grand-nephew"
        if ca_idx == 2:
            return "First Cousin"
        if ca_idx == 3:
            return "Grand-aunt/Grand-uncle"
        else:
            raise ValueError("There is something wrong with the relationship logic.")
    if pl >= 6 and ca_idx == 1:
        return f"Great X{pl-5} Grand-niece/Grand-nephew"
    if pl >= 6 and ca_idx == pl - 2:
        return f"Great X{pl-5} Grand-aunt/Grand-uncle"
    return ""
