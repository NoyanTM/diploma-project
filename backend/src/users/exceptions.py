from fastapi import status

from src.exceptions import BaseHTTPException


class InvalidCredentialsException(BaseHTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Invalid credentials"


class NotAuthenticatedException(BaseHTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "User not authenticated"

    def __init__(self) -> None:
        super().__init__(headers={"WWW-Authenticate": "Bearer"})


class InactiveUserException(BaseHTTPException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "User inactive / deactivated"
    

class InsufficientPermissionsException(BaseHTTPException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Insufficient permissions"


class UserNotFoundException(BaseHTTPException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "User / Users not found"


class UserAlreadyExistsException(BaseHTTPException):
    status_code = status.HTTP_409_CONFLICT
    detail = "User / Users already exists"
