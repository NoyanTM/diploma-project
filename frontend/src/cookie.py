# TODO: seperate cookie logic class CookieHandler - cookie.py

from datetime import datetime

import streamlit as st
import jwt
from extra_streamlit_components import CookieManager


class CookieService():
    def __init__(self):
        self.cookie_service = CookieManager()
    
    def get_access_token(self):
        cookies_list = self.cookie_service.get_all()
        access_token = cookies_list.get("access_token")
        return access_token
    
    def set_access_token(self, token: str):
        decoded_jwt = jwt.decode(
            jwt=token,
            key=st.secrets.JWT_ACCESS_SECRET_KEY,
            algorithms=st.secrets.JWT_ALGORITHM,
        )
        self.cookie_service.set(
            cookie="access_token",
            val=token,
            expires_at=datetime.fromtimestamp(decoded_jwt["exp"]), # .isoformat(), #  Absolute expiration date for the cookie.
            # max_age= Relative max age of the cookie from when the client receives it in seconds.
            # secure=True - only via HTTPS
            same_site = "lax"
        )
        # return decoded_jwt
        