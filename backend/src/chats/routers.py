from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status, Request

from src.postgres import AsyncDep
from src.pagination import Page, paginate, PageParams
from src.auth.dependencies import RBAC, get_current_user
from src.models.users import Role
from src.chats.services import ChatService
from src.chats.schemas import (
    ChatCreate,
    ChatRead,
    ChatUpdate,
    ChatUpdatePartial,
    ChatMessageRead,
    ChatFilterParams,
)
from src.messages.schemas import (
    MessageCreate,
    MessageRead,
)
from src.users.schemas import UserRead

router_chats = APIRouter(
    prefix="/chats",
    tags=["Chats"]
)


# TODO: remake it to maybe "/users/me/chats" instead of just "/chats"???
@router_chats.get(
    "/",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RBAC(Role.USER, Role.MODERATOR, Role.ADMIN))],
    description="Получение списка чатов в формате пагинации, но только текущего пользователя"
)
async def get_chats(
    session: AsyncDep,
    request: Request,
    pagination_params: Annotated[PageParams, Depends(PageParams)],
    filter_params: Annotated[ChatFilterParams, Depends(ChatFilterParams)],
    current_user: Annotated[UserRead, Depends(get_current_user)],
) -> Page[ChatRead]:
    chats = await ChatService(session).get_chats(
        pagination_params=pagination_params,
        filter_params=filter_params,
        current_user=current_user,
    )
    count = await ChatService(session).count_chats(
        filter_params=filter_params,
        current_user=current_user,
    )
    pagination_users = paginate(
        pagination_params=pagination_params,
        total=count,
        results=chats,
        request=request,
    )
    return pagination_users


@router_chats.get(
    "/{chat_uuid}/messages",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RBAC(Role.USER, Role.MODERATOR, Role.ADMIN))],
    description="Получение списка сообщений определенного чата по идентификатору {chat_uuid}, но только текущего пользователя"
)
async def get_current_user_chat_messages_by_uuid(
    session: AsyncDep,
    chat_uuid: UUID,
    current_user: Annotated[UserRead, Depends(get_current_user)],
) -> ChatMessageRead: # list[ChatMessageRead]:
    return await ChatService(session).get_chat_messages_by_uuid(chat_uuid=chat_uuid, current_user=current_user)


@router_chats.post(
    "/{chat_uuid}/messages",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RBAC(Role.USER, Role.MODERATOR, Role.ADMIN))],
    description="Создание нового сообщения в определенном чате по идентификатору {chat_uuid}, но только текущего пользователя"
)
async def create_current_user_chat_message_by_uuid(
    session: AsyncDep,
    chat_uuid: UUID,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    message_data: MessageCreate,
) -> MessageRead: # Response of AI
    return await ChatService(session).create_chat_message_by_uuid(
        chat_uuid=chat_uuid,
        current_user=current_user,
        message_data=message_data,
    )


# @router_chats.get("/{chat_uuid}")
# dependencies=[Depends(RBAC(Role.MODERATOR, Role.ADMIN))]
# get_chat_by_uuid


# get("/user_chats/{user_id}")
# async def get_user_chats(user_id: int):
# cursor.execute("SELECT chat_id FROM chats WHERE user_id=?", (user_id,))


@router_chats.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RBAC(Role.USER, Role.MODERATOR, Role.ADMIN))],
    description="Создание нового чата и привязка его к текущему пользователю"
)
async def create_chat(
    session: AsyncDep,
    chat_data: ChatCreate,
    current_user: Annotated[UserRead, Depends(get_current_user)],
)-> ChatRead:
    return await ChatService(session).create_chat(chat_data=chat_data, current_user=current_user)


@router_chats.put(
    "/{chat_uuid}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RBAC(Role.MODERATOR, Role.ADMIN))]
)
async def update_chat_complete_by_uuid(session: AsyncDep, chat_uuid: UUID, chat_data: ChatUpdate) -> ChatRead:
    return await ChatService(session).update_chat_by_uuid(chat_uuid=chat_uuid, chat_data=chat_data, partial=False)


@router_chats.patch(
    "/{chat_uuid}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RBAC(Role.MODERATOR, Role.ADMIN))]
)
async def update_chat_partial_by_id(session: AsyncDep, chat_uuid: UUID, chat_data: ChatUpdatePartial) -> ChatRead:
    return await ChatService(session).update_chat_by_uuid(chat_uuid=chat_uuid, chat_data=chat_data, partial=True)


@router_chats.delete(
    "/{chat_uuid}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RBAC(Role.MODERATOR, Role.ADMIN))]
)
async def delete_chat_by_uuid(
    session: AsyncDep,
    chat_uuid: UUID,
    soft: bool = None
) -> dict[str, UUID]:
    deleted_chat_uuid = await ChatService(session).delete_chat_by_uuid(chat_uuid=chat_uuid, soft=soft)
    return {"chat_uuid": deleted_chat_uuid}
