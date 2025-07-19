import re
import numpy as np
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


def people_dict() -> dict[str, int]:
    df = st.session_state["data"].copy()
    df = df[[Cols.ID, Cols.NAME, Cols.BIRTHDAY]].replace({np.nan: None})
    people = df[[Cols.ID, Cols.NAME, Cols.BIRTHDAY]].values.tolist()

    def person_string(name: str, birthday: str) -> str:
        return f"{name} ({birthday})" if birthday else name

    def append_or_increment_tag(s, count=2):
        # Pattern to detect [number] at the end of the string
        match = re.search(r"\[(\d+)\]$", s)

        if match:
            # Extract the current number and increment it
            current_num = int(match.group(1)) + 1
            s = re.sub(r"\[\d+\]$", f"[{current_num}]", s)
        else:
            # Append [2] if there's no existing tag
            s += f"[{count}]"

        print(s)  # Display each step if needed
        if count < 10:  # Set a stopping condition to avoid infinite recursion
            return append_or_increment_tag(s, count + 1)
        else:
            return s

    def add_person_to_dict(d: dict, name: str, birthday: str, id: int) -> None:
        key = person_string(name, birthday)
        if key in d:
            # If the key already exists, append a number to make it unique
            key = append_or_increment_tag(key)
        d[key] = id

    person_dict = {}
    for id, name, birthday in people:
        add_person_to_dict(person_dict, name, birthday, id)
    return person_dict
