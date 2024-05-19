# TODO: seperate frontend logic to components (show_sidebar, show_chat, show_user_auth_page) - components
# TODO: change render of show_user_form - add session state - because it renders before access_token is checked
# TODO: page redicrect by session states and st.rerun

import streamlit as st

from src.schemas.users import UserCreate
from src.schemas.auth import UserAuth
from src.api.auth import AuthAPI
from src.api.users import UserAPI
from src.api.chats import ChatAPI


def init_page():
    # Default page configs
    st.set_page_config(
        page_title="Портал АФМ Chatbot",
        page_icon="./src/assets/fma_favicon.png",
        layout="centered",
        initial_sidebar_state="expanded",
    )

    # Delete red line in header of streamlit
    st.markdown(
        """
        <style>
        [data-testid="stDecoration"]
        {
            display: none;
        }
        </style>""",
        unsafe_allow_html=True
    )
    
    # Session states
    if "access_token" not in st.session_state:
        st.session_state["access_token"] = None
    # if "authenticated" not in st.session_state:
    #     st.session_state["authenticated"] = False
    if "chat_button" not in st.session_state:
        st.session_state["chat_button"] = False
    if "chat_button_value" not in st.session_state:
        st.session_state["chat_button_value"] = None
    if "messages" not in st.session_state:
        st.session_state.messages = []


def show_user_form(cookie_service):
    if not st.session_state["access_token"]:
        login_tab, register_tab = st.tabs(["Вход в аккаунт", "Регистрация аккаунта"])
        
        with login_tab:
            with st.form(key = "login_form"):
                st.subheader("Вход на портал МФЦА Chatbot")
                email_input = st.text_input("Почта", placeholder="user@aifc.gov.kz")
                password_input = st.text_input("Пароль", placeholder="************")
                submit_button = st.form_submit_button("Войти")
                if submit_button:
                    token = AuthAPI().create_token(
                        cookie_service,
                        auth_data=UserAuth(
                            username=email_input,
                            password=password_input,
                        ),
                    )
                    st.info(token)
        
        with register_tab:
            with st.form(key = "register_form"):
                st.subheader("Регистрация на портале МФЦА Chatbot")
                name_input = st.text_input("ФИО", placeholder="Иванов Иван Иванович")
                email_input = st.text_input("Почта", placeholder="user@aifc.gov.kz")
                password_input = st.text_input("Пароль", placeholder="************")
                submit_button = st.form_submit_button("Зарегистрироваться")
                if submit_button:
                    user = AuthAPI().register_user(
                        cookie_service,
                        register_data=UserCreate(
                            name=name_input,
                            email=email_input,
                            password=password_input,
                        )
                    )
                    st.info(user)


def show_main_page(token):
    def click_chat_button(button_value):
        st.session_state["chat_button"] = True
        st.session_state["chat_button_value"] = button_value
        
    # if st.session_state
    # with st.sidebar:
    with st.sidebar.container(border=True):
        st.title("Портал МФЦА Chatbot")
        st.image("./src/assets/aifc_logo_transparent.png")
    with st.sidebar.container(border=True):
        user_api = UserAPI(token=token)
        current_user_data = user_api.get_current_user()
        st.text(current_user_data.get("name"))
        st.text(current_user_data.get("email"))
        st.text(current_user_data.get("role"))
        # with st.popover(":gear: Настройки"):
        #     st.text("настройки")
        # logout = st.button(":heavy_multiplication_x: Выйти из аккаунта")
        # if logout:
        # and redicrect # st.rerun() # редиректнуть
    
    with st.sidebar.container(border=True):
        chat_api = ChatAPI(token=token)
        if st.button("Создать новый чат"):
            chat_api.create_chat()
        # with st.popover("Создать новый чат"):
        #     st.text_input("Название чата")
        #     st.text_input("Описание чата")
        
        with st.expander("Список чатов"):
            page_number = st.number_input("Страница списка чатов", min_value=1, step=1)
            current_user_chats = chat_api.get_chats(page_number)            
            for idx, result in enumerate(current_user_chats["results"]):
                chat_button = st.button(result["uuid"], on_click=lambda x: click_chat_button(x), args=[result["uuid"]])
               
    with st.container():
        messages = st.container(height=600)
        if st.session_state["chat_button"]:
            st.session_state.messages = [] # обнулить историю чатов в браузере чтоб в сообщения из одного чата не повторялись в другом чате
            
            st.info(f"Chat UUID: {st.session_state['chat_button_value']}")
            chat_messages = chat_api.get_chat_messages(chat_uuid=st.session_state["chat_button_value"]) 
            for message in chat_messages["message"]:
                if message["additional_metadata"]["tag"] == "user":
                    with messages.chat_message("user"):
                        st.write(message["content"])
                        st.write(message["created_at"])
                if message["additional_metadata"]["tag"] == "bot":
                    with messages.chat_message("assistant"):
                        st.write(message["content"])
                        st.write(message["created_at"])
                        for idx, context in enumerate(message["additional_metadata"]["context"]):
                            with st.expander(context["metadata"]["title"]):
                                source = context["metadata"]["source"]
                                category = context["metadata"]["category"]
                                language = context["metadata"]["language"]
                                st.write(f"Источник: {source}")
                                st.write(f"Тип источника: {category}")
                                st.write(f"Язык источника: {language}")
                                st.write(context["metadata"]["created_at"])
                        
        for message in st.session_state.messages:
            messages.chat_message(message["role"]).write(message["content"])
        if prompt := st.chat_input("Задайте ваш вопрос тут"): 
            st.session_state.messages.append({"role": "user", "content": prompt})
            messages.chat_message("user").write(prompt)
            bot_response = chat_api.create_chat_messages(
                chat_uuid=st.session_state["chat_button_value"],
                content=prompt,
            )
            messages.chat_message("assistant").write(bot_response["content"])
            st.session_state.messages.append({"role": "assistant", "content": bot_response["content"]})
            # TODO: message expander + created_at visualization
        st.selectbox("Выберите тип источника", ("Новости", "События", "Общее"))
        st.selectbox("Выберите язык запроса", ("English", "Русский", "Қазақша"))      
        st.caption("Бот может допускать ошибки, рекомендуется проверять важную информацию. При возникновении любых проблем - сообщайте в техподдержку.")
        