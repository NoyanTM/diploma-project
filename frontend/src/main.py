import streamlit as st

from src.components import (
    init_page,
    show_user_form,
    show_main_page
)
from src.cookie import CookieService


def main():
    init_page()
    
    cookie_service = CookieService()
    access_token = cookie_service.get_access_token()
    st.session_state["access_token"] = access_token
    
    if not access_token:
        show_user_form(cookie_service)
    else:
        show_main_page(token=access_token)
    
    
if __name__ == "__main__":
    main()
    # start from /backend directory with "python -m streamlit run src/main.py"
    