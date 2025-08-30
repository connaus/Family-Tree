# Family Tree App

This Streamlit app displays and manages a family tree, designed for a specific family gathering. The app is password protected and allows users to view, add, and edit family members, visualize relationships, and explore the full descendant tree.
This app is published [here](https://family-tree.streamlit.app/). 

## Features

- **Tree Navigation:** View a specific descendant, their children, and spouse(s).
- **Full Tree View:** See the entire family tree as a list or interactive graph.
- **Add/Edit Person:** Add new family members or edit existing ones, including relationships and key dates.
- **Relationship Highlighting:** Highlight and explore relationships between any two people.
- **Authentication:** Password-protected access using [Streamlit Authenticator](https://github.com/mkhorasani/Streamlit-Authenticator).
- **Google Sheets Integration:** Data is read from and written to a Google Sheet for easy collaboration. Instructions can be found [here](https://docs.streamlit.io/develop/tutorials/databases/private-gsheet)

## Getting Started

### Prerequisites

- Python 3.10+
- [Streamlit](https://streamlit.io/)
- Google Sheets credentials (see below)

### Installation

1. Clone the repository:
    ```sh
    git clone <repo-url>
    cd family_tree
    ```

2. Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```

3. Configure Streamlit secrets:
    - Copy your Google Sheets and authentication credentials into `.streamlit/secrets.toml`.
    - See `.gitignore` to ensure secrets are not committed.

4. (Optional) Adjust `.streamlit/config.toml` for theme settings.

### Running the App

Start the app with:

```sh
streamlit run app.py
```
Or use the provided batch file on Windows:
[start.bat](http://_vscodecontentref_/1)

# Usage
- Login: Enter your username and password.
- Navigate: Use the dropdown to select a person, view their details, or switch to the full tree view.
- Add/Edit: Use the "Add Child", "Add Spouse", or "Edit" buttons to modify the tree.
- Highlight Relationships: Use the "Show Relationships" button to highlight lineage paths.
# File Structure
- app.py — Main navigation page.
- pages/1_Add_person.py — Add or edit a person.
- pages/Full_Tree.py — Full tree visualization.
- src/ — Core logic (data handling, authentication, visualization).
- cfg/table_schema.py — Data schema definitions.
- .streamlit/ — Streamlit configuration and secrets.
# Updating Password
- To update the password, modify the credentials in .streamlit/secrets.toml.

# License
This project is for private use and not intended for public distribution.