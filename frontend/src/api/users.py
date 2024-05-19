import httpx
import streamlit as st

from src.schemas.users import UserCreate, UserRead
from src.schemas.auth import UserAuth
from src.schemas.enums import ErrorMessage

class UserAPI():
    def __init__(self, token: str):
        self.base_url = st.secrets.BASE_URL + "/users"
        self.token = token

    def get_current_user(self):
        response = httpx.get(
            url = self.base_url + "/me",
            headers = {"authorization": f"Bearer {self.token}"}
        )
        if response.status_code == 200:
            return response.json()
        else:
            return ErrorMessage.INTERNAL_SERVER_ERROR
    