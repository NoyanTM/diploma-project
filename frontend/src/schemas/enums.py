# from enum import Enum


class ErrorMessage(str): # Enum
    INTERNAL_SERVER_ERROR = "Ошибка со стороны сервера" # 500
    VALIDATION_ERROR = "Ошибка валидации или проверки данных" # 422
    NOT_FOUND = "Не найдено" # 404
    INVALID_CREDENTIALS = "Неверная почта или пароль" # 
    UNAUTHORIZED = "Не авторизован" # 401
