import numpy as np
import pandas as pd
import streamlit as st
from cfg.table_schema import Cols
from src import data_funcs

# set up
id = st.session_state.get("editing_id", None)
df = st.session_state["data"].copy()
people_dict = data_funcs.people_dict()
rev_people_dict = {v: k for k, v in people_dict.items()}
people = list(people_dict.keys())
people.sort()

if id is None:
    row = pd.Series(index=st.session_state["data"].columns)
    row[Cols.ID] = df[Cols.ID].max() + 1
    row = row.replace({np.nan: None})
    parent = st.session_state.get("add_child", None)
    spouse = st.session_state.get("add_spuose", None)
    if parent is not None:
        row[Cols.PARENT] = people_dict.get(parent, None)
    if spouse is not None:
        row[Cols.SPOUSE] = people_dict.get(spouse, None)
else:
    row = df[df[Cols.ID] == id]
    if isinstance(row, pd.DataFrame):
        row = row.iloc[0]
row = row.replace({np.nan: None})


def text_input(title: str, key: Cols):
    left, right = st.columns([1, 2])
    left.markdown(f"# {title}")
    right.text_input(
        " ", key=f"add_{key}", value=row.get(key), label_visibility="hidden"
    )


def selectbox(title: str, key: Cols, options: list[str]):
    sb_id = row.get(key)
    if id is not None and sb_id is not None:
        start_id = int(sb_id)
        start_name = rev_people_dict[start_id]
        # parent_name = df[df[Cols.ID] == parent_id][Cols.NAME].values[0]
        start_value = people.index(start_name)
    else:
        start_value = None
    left, right = st.columns([1, 2])
    left.markdown(f"# {title}")
    right.write(" ")
    right.write(" ")
    right.selectbox(
        "Select Parent",
        options=options,
        index=start_value,
        key=f"add_{key}",
        label_visibility="collapsed",
    )


st.markdown("# Enter Person Details")
text_input("Name", Cols.NAME)

selectbox("Parent", Cols.PARENT, people)

selectbox("Spouse", Cols.SPOUSE, people)

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

# st.markdown("## Birth Date\n\nEnter in any Format")
text_input("Birth Date", Cols.BIRTHDAY)
# st.markdown("## Birth Place")
text_input("Birth Place", Cols.BIRTHPLACE)

if st.session_state.get(f"add_{Cols.SPOUSE}", ""):
    # st.markdown("## Marriage Date")
    text_input("Marriage Date", Cols.MARRIAGEDATE)


def add_value_to_row(key: Cols):
    """Add a value to the row based on the key."""
    if key in (Cols.PARENT, Cols.SPOUSE):
        value = st.session_state.get(f"add_{key}")
        if value is not None:
            # Convert to ID if it's a name
            if isinstance(value, str) and value in people_dict:
                row[key] = people_dict[value]
            else:
                row[key] = value
    else:
        value = st.session_state.get(f"add_{key}")
        if value is not None:
            row[key] = value


st.markdown("---")
left, middle, right = st.columns([1, 1, 1])
if left.button("Save Changes", key="save_changes"):
    add_value_to_row(Cols.NAME)
    add_value_to_row(Cols.NAME)
    add_value_to_row(Cols.PARENT)
    add_value_to_row(Cols.SPOUSE)
    add_value_to_row(Cols.BIRTHDAY)
    add_value_to_row(Cols.BIRTHPLACE)
    if st.session_state.get(f"add_{Cols.SPOUSE}", ""):
        add_value_to_row(Cols.MARRIAGEDATE)

    if st.session_state.get("editing_id", None) is not None:
        df[df[id] == id] = row
    else:
        df = pd.concat([df, pd.DataFrame([row.to_dict()])], ignore_index=True)
    st.markdown(":green[Changes saved successfully!]")
elif right.button("Cancel", key="cancel_add_person"):
    st.switch_page("app.py")
st.page_link("app.py")
st.dataframe(row.to_frame().T, use_container_width=True)
st.dataframe(df, use_container_width=True)
