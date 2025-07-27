import re
import time
import numpy as np
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import streamlit as st

from cfg.table_schema import Cols


class Data:
    def __init__(self, worksheet: str = "Sheet1"):
        self.conn = st.connection("gsheets", type=GSheetsConnection)
        self.worksheet = worksheet
        self._df: pd.DataFrame | None = None
        self._person_to_id_map: dict[str, int] | None = None
        self._id_to_person_map: dict[int, str] | None = None
        self._people: list[str] | None = None

    def read(self):
        self._df = self.conn.read(
            worksheet=self.worksheet,
            dtype={
                Cols.BIRTHDAY: str,
                Cols.DEATHDATE: str,
                Cols.MARRIAGEDATE: str,
            },
            ttl=1,
        )
        self._df.set_index("id", inplace=True, drop=False)
        return self._df

    def update(self, data=None):
        if data is not None:
            self.conn.update(worksheet=self.worksheet, data=data)
            time.sleep(1)
            self.read()

    @property
    def df(self) -> pd.DataFrame:
        if self._df is None:
            self._df = self.read()
            self._df.replace({np.nan: None}, inplace=True)
            self._person_to_id_map = None
            self._id_to_person_map = None
            self._df.set_index("id", inplace=True, drop=False)
        return self._df

    @df.setter
    def df(self, value: pd.DataFrame) -> None:
        """Set the DataFrame and reset the cached maps."""
        self.update(value)
        self._person_to_id_map = None
        self._id_to_person_map = None
        self._people = None

    @property
    def person_to_id_map(self) -> dict[str, int]:
        """Create a dictionary of people with their names and birthdays as the key and their IDs as the value.
        EAch name is unique wthe a DOB added, and a nuber added after if that is required.
        """
        if self._person_to_id_map is not None:
            return self._person_to_id_map
        df = self.df.copy()
        people = df[[Cols.ID, Cols.NAME, Cols.BIRTHDAY]].values.tolist()

        def person_string(name: str, birthday: str) -> str:
            return f"{name} ({birthday})" if birthday else name

        def append_or_increment_tag(key: str, d: dict[str, int], count=2):
            # Pattern to detect [number] at the end of the string
            match = re.search(r"\[(\d+)\]$", key)

            if match:
                # Extract the current number and increment it
                current_num = int(match.group(1)) + 1
                key = re.sub(r"\[\d+\]$", f"[{current_num}]", key)
            else:
                # Append [2] if there's no existing tag
                key += f"[{count}]"

            print(key)  # Display each step if needed
            if (
                key in d and count < 10
            ):  # Set a stopping condition to avoid infinite recursion
                return append_or_increment_tag(key, d, count + 1)
            else:
                return key

        def add_person_to_dict(d: dict, name: str, birthday: str, id: int) -> None:
            key = person_string(name, birthday)
            if key in d:
                # If the key already exists, append a number to make it unique
                key = append_or_increment_tag(key, d, count=2)
            d[key] = id

        person_dict = {}
        for id, name, birthday in people:
            add_person_to_dict(person_dict, name, birthday, id)
        self._person_to_id_map = person_dict
        return self._person_to_id_map

    @property
    def id_to_person_map(self) -> dict[int, str]:
        """Create a dictionary of IDs with their names and birthdays as the value."""
        if self._id_to_person_map is not None:
            return self._id_to_person_map
        self._id_to_person_map = {v: k for k, v in self.person_to_id_map.items()}
        return self._id_to_person_map

    def people(
        self, descendants_only=True, remove_ids: int | list[int] = []
    ) -> list[str]:
        """Get a sorted list of people names. Setting descendants only to False gives all names,
        True return only people with a direct lineage to the first person."""
        df = self.df.copy()
        if descendants_only:
            df = df[(pd.notna(df[Cols.PARENT])) | (df[Cols.ID] == 0)]
        if remove_ids:
            if isinstance(remove_ids, int):
                remove_ids = [remove_ids]
            df = df[~df[Cols.ID].isin(remove_ids)]
        people = df[Cols.ID].values.tolist()
        return [self.id_to_person_map[i] for i in people]

    def person_index(self, id: int) -> int:
        """get the index of the person corresponding to the given id"""
        return (
            self.people(descendants_only=False).index(self.id_to_person_map[id])
            if id in self.id_to_person_map
            else 0
        )
