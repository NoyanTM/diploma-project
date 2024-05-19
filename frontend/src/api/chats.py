import httpx
import streamlit as st

from src.schemas.users import UserCreate, UserRead
from src.schemas.auth import UserAuth
from src.schemas.enums import ErrorMessage


class ChatAPI():
    def __init__(self, token: str):
        self.base_url = st.secrets.BASE_URL + "/chats"
        self.token = token
    
    def get_chats(self, page):
        response = httpx.get(
            url = self.base_url + "/",
            headers = {"authorization": f"Bearer {self.token}"},
            params = {"page": f"{page}", "size": 10, "order": "desc"}
        )
        if response.status_code == 200:
            return response.json()
        else:
            return ErrorMessage.INTERNAL_SERVER_ERROR
    
    def create_chat(self):
        response = httpx.post(
            url = self.base_url + "/",
            headers = {"authorization": f"Bearer {self.token}"},
            json = {},
        )
        if response.status_code == 200:
            return response.json()
        else:
            return ErrorMessage.INTERNAL_SERVER_ERROR
    
    def get_chat_messages(self, chat_uuid):
        response = httpx.get(
            url = self.base_url + f"/{chat_uuid}/messages",
            headers = {"authorization": f"Bearer {self.token}"},
        )
        if response.status_code == 200:
            return response.json()
        else:
            return ErrorMessage.INTERNAL_SERVER_ERROR
    
    def create_chat_messages(self, chat_uuid, content): # query_type
        response = httpx.post(
            url = self.base_url + f"/{chat_uuid}/messages",
            headers = {"authorization": f"Bearer {self.token}"},
            # params = {"query_type": f"{query_type}"},
            json = {"content": f"{content}"},
            timeout = None,
        )
        if response.status_code == 201:
            return response.json()
        else:
            return ErrorMessage.INTERNAL_SERVER_ERROR
        