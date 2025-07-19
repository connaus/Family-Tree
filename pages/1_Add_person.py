import numpy as np
import pandas as pd
import streamlit as st
from cfg.table_schema import Cols
from src import data_funcs

st.markdown("# Enter Person Details")

id = st.session_state.get("editing_id", None)
df = st.session_state["data"].copy()
people_dict = data_funcs.people_dict()
people = list(people_dict.keys())
if id is None:
    row = pd.Series(index=st.session_state["data"].columns)
    row[Cols.ID] = df[Cols.ID].max() + 1
    row = row.replace({np.nan: None})
else:
    row = df[df[Cols.ID] == id]
    row = row.replace({np.nan: None})


def text_input(key: Cols):
    st.text_input(" ", key=f"add_{key}", value=row.get(key), label_visibility="hidden")


def selectbox(key: Cols, options: list[str]):
    sb_id = row.get(key)
    if id is not None:
        parent_id = int(sb_id)
        parent_name = df[df[Cols.ID] == parent_id][Cols.NAME].values[0]
        start_value = people.index(parent_name)
    else:
        start_value = None
    st.selectbox(
        "Select Parent",
        options=options,
        index=start_value,
        key=f"add_{key}",
    )


st.markdown("## Name")
text_input(Cols.NAME)

st.markdown("## Parent")
selectbox(Cols.PARENT, people)

st.markdown("## Spouse")
selectbox(Cols.SPOUSE, people)

if not (
    st.session_state.get(f"add_{Cols.NAME}") is not None
    and (
        st.session_state.get(f"add_{Cols.PARENT}") is not None
        or st.session_state.get(f"add_{Cols.SPOUSE}") is not None
    )
):
    st.info(
        "A name must be entered and one of either Parent or Spouse must be selected."
    )
    st.stop()

st.markdown("## Birth Date\n\nEnter in any Format")
text_input(Cols.BIRTHDAY)
st.markdown("## Birth Place")
text_input(Cols.BIRTHPLACE)

if st.session_state.get(f"add_{Cols.SPOUSE}", ""):
    st.markdown("## Marriage Date")
    text_input(Cols.MARRIAGEDATE)
