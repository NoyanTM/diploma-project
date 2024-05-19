from fastapi import status

from src.exceptions import BaseHTTPException


class ChatNotFoundException(BaseHTTPException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Chat / Chats not found"


class ChatAlreadyExistsException(BaseHTTPException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Chat / Chats already exists"


class ChatMessageLLMInternalException(BaseHTTPException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Cannot generate LLM response"


class ChatMessageLLMInternalException(BaseHTTPException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Cannot connect to Neo4j"


# "Данных по вашему запросу нет", "Сформулируйте вопрос корректнее", "Пожалуйста, сформулируйте вопрос точнее", 
        # Сформулируйте вопрос корректнее, "Нет данных", "except IncorrectIINException"