from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm

from src.postgres import AsyncDep
from src.auth.services import AuthService
from src.users.services import UserService
from src.auth.dependencies import RBAC, get_current_user
from src.models.users import Role
from src.auth.schemas import (
    Token,
    UserAuth,
    TokenData,
)
from src.users.schemas import UserRead, UserCreate
from src.config import settings

router_auth = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router_auth.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    session: AsyncDep,
    user_data: UserCreate,
) -> UserRead:
    return await UserService(session).create_user(user_data=user_data)


@router_auth.post(
    "/create-token", # /login
    status_code=status.HTTP_200_OK,
)
async def generate_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncDep,
    response: Response
) -> Token:
    token = await AuthService(session).generate_token(form_data.username, form_data.password)
    response.set_cookie(
        "access_token",
        token.access_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_SECONDS,
        httponly=True,
    )
    return token

# TODO:
# @router_auth.post(
#     "/refresh-token",
#     status_code=status.HTTP_200_OK,
# )
# async def refresh_token()

@router_auth.post(
    "/delete-token", # /logout
    status_code=status.HTTP_200_OK,
)
async def delete_token(
    # request: Request,
    response: Response,
    # current_user: Annotated[UserRead, Depends(get_current_user)],
) -> dict[str, str]:
    response.delete_cookie("access_token")
    return {"message": "cookie deleted"}
    # return {"user_uuid": current_user.uuid}
