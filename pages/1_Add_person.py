import numpy as np
import pandas as pd
import streamlit as st
from cfg.table_schema import Cols
from src.data import Data

# set up
id = st.session_state.get("editing_id", None)
parent = st.session_state.get("add_child", None)
spouse = st.session_state.get("add_spouse", None)
data: Data = st.session_state.get("data", Data())
df: pd.DataFrame = data.df.copy()

if st.session_state.get("edit_row", None) is not None:
    row: pd.Series = st.session_state["edit_row"]
elif id is None:
    row = pd.Series(index=df.columns)
    if parent is not None:
        row[Cols.PARENT] = parent
    if spouse is not None:
        row[Cols.SPOUSE] = spouse
else:
    st.session_state["original_row"] = df[df[Cols.ID] == id].iloc[0]
    row = df[df[Cols.ID] == id].iloc[0]
row = row.replace({np.nan: None})


def text_input(title: str, key: Cols):
    left, right = st.columns([1, 2])
    left.markdown(f"# {title}")
    right.text_input(
        " ", key=f"add_{key}", value=row.get(key), label_visibility="hidden"
    )


def selectbox(title: str, key: Cols, options: list[str]):
    sb_id = row.get(key)
    if sb_id is not None:
        start_id = int(sb_id)
        start_name = data.id_to_person_map[start_id]
        # parent_name = df[df[Cols.ID] == parent_id][Cols.NAME].values[0]
        start_value = data.people.index(start_name)
    else:
        start_value = None
    left, middle, right = st.columns([2, 3, 1])
    left.markdown(f"# {title}")
    middle.write(" ")
    middle.write(" ")

    def update_row():
        row[key] = data.person_to_id_map[st.session_state[f"add_{key}_selectbox"]]

    middle.selectbox(
        "Select Parent",
        options=options,
        index=start_value,
        key=f"add_{key}_selectbox",
        label_visibility="collapsed",
        on_change=update_row,
    )
    right.write(" ")
    right.write(" ")
    right.button(
        "Clear Selection",
        key=f"clear_{key}",
        use_container_width=True,
        on_click=lambda: st.session_state.update({f"add_{key}_selectbox": None}),
    )


if st.button("Go Back to Tree", key="return_to_tree"):
    st.switch_page("app.py")
    st.session_state["edit_row"] = None
st.markdown("# Enter Person Details")
text_input("Name", Cols.NAME)

selectbox("Parent", Cols.PARENT, data.people)

selectbox("Spouse", Cols.SPOUSE, data.people)

if not (
    st.session_state.get(f"add_{Cols.NAME}") is not None
    and (
        st.session_state.get(f"add_{Cols.PARENT}_selectbox") is not None
        or st.session_state.get(f"add_{Cols.SPOUSE}_selectbox") is not None
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

if st.session_state.get(f"add_{Cols.SPOUSE}_selectbox", ""):
    # st.markdown("## Marriage Date")
    text_input("Marriage Date", Cols.MARRIAGEDATE)

st.session_state["edit_row"] = row


def add_value_to_row(key: Cols):
    """Add a value to the row based on the key."""
    if key in (Cols.PARENT, Cols.SPOUSE):
        value = st.session_state.get(f"add_{key}_selectbox")
        # Convert to ID if it's a name
        if isinstance(value, str) and value in data.person_to_id_map:
            row[key] = data.person_to_id_map[value]
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
    add_value_to_row(Cols.MARRIAGEDATE)
    # update data to ensure that we are changing the latest available data
    current_data = data.read()
    if st.session_state.get("editing_id", None) is not None:
        saved_row: pd.Series = current_data[current_data["id"] == id].iloc[0]
        if not saved_row.equals(st.session_state["original_row"]):
            st.markdown(
                ":green[No changes made to the data as it has been updated by another user! Please try again later.]"
            )
            st.session_state.update(
                {
                    "editing_id": None,
                    "add_child": None,
                    "add_spouse": None,
                }
            )
            st.stop()
        df[df["id"] == id] = row
    else:
        row[Cols.ID] = int(current_data[Cols.ID].max() + 1)
        df = pd.concat([df, pd.DataFrame([row.to_dict()])], ignore_index=True)
    data.df = df
    st.session_state.update(
        {
            "original_row": None,
            "editing_id": None,
            "add_child": None,
            "add_spouse": None,
        }
    )
    st.switch_page("app.py")
if right.button("Cancel", key="cancel_add_person"):
    st.switch_page("app.py")
    st.session_state["edit_row"] = None
