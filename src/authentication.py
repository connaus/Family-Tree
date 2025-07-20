from dataclasses import dataclass
import streamlit as st
import streamlit_authenticator as stauth


@dataclass
class Authenticator:

    _username: str | None = None
    _auth_dict: dict[str, dict[str, dict[str, str]]] | None = None
    _authenticator: stauth.Authenticate | None = None

    @property
    def username(self) -> str:
        if self._username is not None:
            return self._username
        un: str = list(dict(st.secrets["credentials"]["usernames"]).keys())[
            0
        ]  # assumes only one user
        self._username = un
        return self._username

    @property
    def auth_dict(self) -> dict[str, dict[str, dict[str, str]]]:
        if self._auth_dict is not None:
            return self._auth_dict
        self._auth_dict = {
            "usernames": {
                self.username: dict(
                    st.secrets["credentials"]["usernames"][self.username]
                )
            }
        }
        return self._auth_dict

    @property
    def authenticator(self) -> stauth.Authenticate:
        if self._authenticator is not None:
            return self._authenticator
        self._authenticator = stauth.Authenticate(
            self.auth_dict,
            st.secrets["cookie"]["name"],
            st.secrets["cookie"]["key"],
            st.secrets["cookie"]["expiry_days"],
        )
        return self._authenticator

    def _currently_logged_in(self) -> bool:
        """Check if the user is currently logged in."""
        return st.session_state.get("authentication_status", None) is not None

    def check_login(self):
        if self._currently_logged_in():
            return
        self.authenticator.login()
        if st.session_state["authentication_status"] is None:
            st.warning("Please enter the username and password to log in.")
            st.stop()

        if not st.session_state["authentication_status"]:
            st.error("Username/password is incorrect")
            st.stop()
