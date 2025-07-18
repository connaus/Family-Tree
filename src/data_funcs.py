import pandas as pd
import streamlit as st

from cfg.table_schema import Cols


def get_person_details(id: int | list[int]) -> pd.DataFrame | pd.Series:
    """retreive the row of the person with the id"""
    df: pd.DataFrame = st.session_state["data"].copy()
    person = df.iloc[id]
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
    df: pd.DataFrame = st.session_state["data"].copy()
    df = df[df[Cols.SPOUSE] == id]
    if df.empty:
        return None
    return df


def find_children(id: int) -> pd.DataFrame | None:
    """find the spouse of a person by id"""
    df: pd.DataFrame = st.session_state["data"].copy()
    df = df[df[Cols.PARENT] == id]
    if df.empty:
        return None
    return df
