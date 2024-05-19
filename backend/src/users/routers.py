from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status, Request, BackgroundTasks

from src.postgres import AsyncDep
from src.users.services import UserService
from src.models.users import Role
from src.auth.dependencies import RBAC, get_current_user
from src.pagination import Page, PageParams, paginate
from src.users.schemas import (
    UserFilterParams,
    UserRead,
    UserCreate,
    UserUpdate,
    UserUpdatePartial,
)

router_users = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router_users.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RBAC(Role.ADMIN))]
)
async def create_user(session: AsyncDep, user_data: UserCreate) -> UserRead:
    return await UserService(session).create_user(user_data=user_data)


@router_users.get(
    "/",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RBAC(Role.MODERATOR, Role.ADMIN))]
)
async def get_users(
    session: AsyncDep,
    request: Request,
    pagination_params: Annotated[PageParams, Depends(PageParams)],
    filter_params: Annotated[UserFilterParams, Depends(UserFilterParams)],
) -> Page[UserRead]:
    users = await UserService(session).get_users(
        pagination_params=pagination_params,
        filter_params=filter_params,
    )
    count = await UserService(session).count_users(
        filter_params=filter_params,
    )
    pagination_users = paginate(
        pagination_params=pagination_params,
        total=count,
        results=users,
        request=request,
    )
    return pagination_users


@router_users.get(
    "/me",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RBAC(Role.USER, Role.MODERATOR, Role.ADMIN))]
)
async def get_user_me(current_user: Annotated[UserRead, Depends(get_current_user)]) -> UserRead:
    return current_user


@router_users.put(
    "/me",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RBAC(Role.ADMIN))]
)
async def update_user_me(
    session: AsyncDep,
    user_data: UserUpdate,
    current_user: Annotated[UserRead, Depends(get_current_user)],
) -> UserRead:
    return await UserService(session).update_user_by_uuid(user_uuid=current_user.uuid, user_data=user_data, partial=False)


@router_users.patch(
    "/me",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RBAC(Role.ADMIN))]
)
async def update_user_partial_me(
    session: AsyncDep,
    user_data: UserUpdatePartial,
    current_user: Annotated[UserRead, Depends(get_current_user)],
) -> UserRead:
    return await UserService(session).update_user_by_uuid(user_uuid=current_user.uuid, user_data=user_data, partial=True)


@router_users.delete(
    "/me",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RBAC(Role.ADMIN))],
)
async def delete_user_me(
    session: AsyncDep,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    soft: bool = None,
) -> dict[str, UUID]:
    delete_user_uuid = await UserService(session).delete_user_by_uuid(user_uuid=current_user.uuid, soft=soft)
    return {"user_uuid": delete_user_uuid}


@router_users.get(
    "/{user_uuid}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RBAC(Role.MODERATOR, Role.ADMIN))]
)
async def get_user_by_uuid(session: AsyncDep, user_uuid: UUID) -> UserRead:
    return await UserService(session).get_user_by_uuid(user_uuid=user_uuid)


@router_users.put(
    "/{user_uuid}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RBAC(Role.ADMIN))]
)
async def update_user_complete_by_uuid(session: AsyncDep, user_uuid: UUID, user_data: UserUpdate) -> UserRead:
    return await UserService(session).update_user_by_uuid(user_uuid=user_uuid, user_data=user_data, partial=False)


@router_users.patch(
    "/{user_uuid}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RBAC(Role.ADMIN))]
)
async def update_user_partial_by_uuid(session: AsyncDep, user_uuid: UUID, user_data: UserUpdatePartial) -> UserRead:
    return await UserService(session).update_user_by_uuid(user_uuid=user_uuid, user_data=user_data, partial=True)


@router_users.delete(
    "/{user_uuid}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RBAC(Role.ADMIN))],
)
async def delete_user_by_uuid(
    session: AsyncDep,
    user_uuid: UUID,
    soft: bool = None,
) -> dict[str, UUID]:
    deleted_user_uuid = await UserService(session).delete_user_by_uuid(user_uuid=user_uuid, soft=soft)
    return {"user_uuid": deleted_user_uuid}
