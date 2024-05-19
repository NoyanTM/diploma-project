# TODO: add try except to httpx requests or whole class for httpx wrapper

import httpx
import streamlit as st

from src.schemas.users import UserCreate
from src.schemas.auth import UserAuth
from src.schemas.enums import ErrorMessage


class AuthAPI():
    def __init__(self): # token: str
        self.base_url = st.secrets.BASE_URL + "/auth"
        # self.token = token
    
    def register_user(self, cookie_service, register_data: UserCreate):
        response = httpx.post(
            url = self.base_url + "/register",
            json = register_data.model_dump()
        )
        if response.status_code == 201:
            # создать токен для пользователя автоматически и проверить + return True + redirect
            user_data = register_data.model_dump()
            token = self.create_token(
                cookie_service,
                auth_data=UserAuth(
                    username=user_data["email"],
                    password=user_data["password"],
                )
            )
            return token # response.json(), token
        if response.status_code == 422:
            validation_errors_json = response.json()
            errors_set = set()
            for error in validation_errors_json["detail"]:
                errors_set.add(error["msg"])
            return errors_set # return ErrorMessage.VALIDATION_ERROR
        else:
            return ErrorMessage.INTERNAL_SERVER_ERROR
    
    def create_token(self, cookie_service, auth_data: UserAuth):
        response = httpx.post(
            url = self.base_url + "/create-token",
            data = auth_data.model_dump(),
            headers={"content-type": "application/x-www-form-urlencoded"},
        )
        if response.status_code == 200:
            body = response.json()
            token = body.get("access_token")
            cookie_service.set_access_token(token)
            # st.session_state["authenticated"] = True
            return token
        if response.status_code == 422:
            return ErrorMessage.VALIDATION_ERROR
        else:
            return ErrorMessage.INTERNAL_SERVER_ERROR

    def delete_token(self):
        response = httpx.post(
            url = self.base_url + "/delete-token",
        )
        if response.status_code == 200:
            return True
        else:
            return False
    