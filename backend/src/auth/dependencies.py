from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError

from src.users.services import UserService
from src.auth.jwt import JWT
from src.auth.schemas import TokenData
from src.users.schemas import UserRead
from src.config import settings
from src.postgres import AsyncDep
from src.users.exceptions import (
    NotAuthenticatedException,
    InsufficientPermissionsException,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/create-token') # /auth/login


async def get_token_payload(
    token: Annotated[str, Depends(oauth2_scheme)]
):
    try:
        payload = JWT.decode_jwt(
            secret_key=settings.ACCESS_SECRET_KEY,
            token=token
        )
    except PyJWTError:
        raise NotAuthenticatedException
    return payload


async def get_current_user( # merged with get_current_active_user
    session: AsyncDep,
    payload: Annotated[dict, Depends(get_token_payload)],
) -> UserRead:
    username = payload.get("sub")
    if username is None: 
        raise NotAuthenticatedException
    token_data = TokenData(username=username)
    user = await UserService(session).get_user_by_email(user_email=token_data.username)
    if user is None:
        raise NotAuthenticatedException
    if not user.is_active:
        raise NotAuthenticatedException
    return user


class RBAC:
    def __init__(self, *allowed_roles):
        self.allowed_roles = allowed_roles
    
    def __call__(self, current_user: Annotated[UserRead, Depends(get_current_user)]):
        if current_user.role not in self.allowed_roles:
            raise InsufficientPermissionsException
        return True
