from uuid import UUID
from datetime import datetime
import json

from sqlalchemy import func, select, insert, delete, update, asc, desc
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.encoders import jsonable_encoder

from src.models.chats import Chat
from src.models.messages import Message
from src.pagination import OrderEnum, PageParams
from src.users.schemas import UserRead
from src.chats.schemas import (
    ChatCreate,
    ChatRead,
    ChatUpdate,
    ChatUpdatePartial,
    ChatMessageRead,
    ChatFilterParams,
    Document
)
from src.messages.schemas import (
    MessageCreate,
    MessageRead,
)
from src.chats.exceptions import (
    ChatAlreadyExistsException,
    ChatNotFoundException,
    ChatMessageLLMInternalException,
)
from src.users.exceptions import (
    InsufficientPermissionsException
)
from src.chats.llm import LLMService


class ChatService():    
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
    
    async def get_chat_by_uuid(self, chat_uuid: UUID) -> Chat:
        select_stmt = select(Chat).where(Chat.uuid == chat_uuid)
        select_res = await self.session.execute(select_stmt)
        chat = select_res.scalar_one_or_none()
        if chat is None:
            raise ChatNotFoundException
        return chat
    
    # TODO: also better to make to make get_chat_by_title or get_chats_by_title in
    # elasticsearch or postgres fuzzy / full text search + при обновлении чата нужно только изменить название чата
    
    async def get_chats(
        self,
        current_user: UserRead,
        pagination_params: PageParams,
        filter_params: ChatFilterParams | None = None,
    ) -> list[ChatRead] | None:
        select_stmt = (
            select(Chat)
            .where(
                Chat.is_active == filter_params.is_active if filter_params.is_active else True,
                Chat.user_uuid == current_user.uuid,
            )
            .order_by(
                asc(Chat.created_at)
                if pagination_params.order is OrderEnum.ASC
                else desc(Chat.created_at)
            )
            .limit(pagination_params.size)
            .offset(
                pagination_params.page - 1
                if pagination_params.page == 1
                else (pagination_params.page - 1) * pagination_params.size
            )
        )
        select_res = await self.session.execute(select_stmt)
        users_models = select_res.scalars().all()
        users_schemas = [ChatRead.model_validate(users_model) for users_model in users_models]
        return users_schemas
    
    async def count_chats(
        self,
        current_user: UserRead,
        filter_params: ChatFilterParams | None = None,
    ) -> int | None:
        select_stmt = (
            select(func.count())
            .select_from(Chat)
            .where(
                Chat.is_active == filter_params.is_active if filter_params.is_active else True,
                Chat.user_uuid == current_user.uuid,
            )
        )
        select_res = await self.session.execute(select_stmt)
        count = select_res.scalar()
        return count

    async def get_chat_messages_by_uuid(
        self,
        current_user: UserRead,
        chat_uuid: UUID,
    ) -> ChatMessageRead:
        select_stmt = select(Chat).options(selectinload(Chat.message)).where(Chat.uuid == chat_uuid)
        select_res = await self.session.execute(select_stmt)
        chat_messages = select_res.scalar_one_or_none() # .scalars().all()
        if chat_messages.user_uuid != current_user.uuid:
            raise InsufficientPermissionsException
        # if not chat_messages:
        #     raise ChatNotFoundException
        chat_messages_dto = ChatMessageRead.model_validate(chat_messages) # [ChatMessageRead.model_validate(row) for row in chat_messages]
        return chat_messages_dto
    
    # TODO: check this function again - need refactoring
    async def create_chat_message_by_uuid(
        self,
        current_user: UserRead,
        chat_uuid: UUID,
        message_data: MessageCreate,
    ) -> MessageRead: # Response of AI
        select_stmt = select(Chat).where(Chat.uuid == chat_uuid, Chat.user_uuid == current_user.uuid)
        select_res = await self.session.execute(select_stmt)
        chat = select_res.scalar_one_or_none()
        if chat is None:
            raise ChatNotFoundException
        message_dict = message_data.model_dump()
        
        # create message of user
        insert_stmt = insert(Message).values(
            **message_dict,
            chat_uuid=chat_uuid,
            additional_metadata={"tag": "user"}, # "request_type": f"{query_type}" tag:user, tag:bot, request_type:text-to-sql-query-qa, request_type:qa
        ).returning(Message)
        insert_res = await self.session.execute(insert_stmt)
        await self.session.commit()
        # new_message = insert_res.scalars().first()
        # return new_message
        
        # create message of chatbot
        try:
            rag_response = LLMService.init_rag_chain(question_text=message_dict.get("content"))
        except ChatMessageLLMInternalException as e:
            raise e # print(e)
        
        # TODO: optimize this part
        context_data = rag_response["context"]
        jsonable_list = []
        for idx, item in enumerate(context_data):
            jsonable_instance = json.dumps(jsonable_encoder(context_data[idx]))
            jsonable_list.append(jsonable_instance)
        jsonable_models = [Document.model_validate_json(row) for row in jsonable_list]
        jsonable_dict = [jsonable_model.model_dump() for jsonable_model in jsonable_models]
        # context_json_list = json.dumps(jsonable_dict, ensure_ascii=False, indent=4)
        
        insert_stmt = insert(Message).values(
            content=rag_response["answer"],
            chat_uuid=chat_uuid,
            additional_metadata={"tag": "bot", "context": jsonable_dict} # TODO: nested json bug here, because initially it was with page_context also json
        ).returning(Message)
        insert_res = await self.session.execute(insert_stmt)
        await self.session.commit()
        new_message = insert_res.scalars().first()
        return new_message
    
    async def create_chat(
        self,
        current_user: UserRead,
        chat_data: ChatCreate,
    ) -> Chat:
        chat_dict = chat_data.model_dump()
        insert_stmt = insert(Chat).values(**chat_dict, user_uuid=current_user.uuid).returning(Chat)
        insert_res = await self.session.execute(insert_stmt)
        await self.session.commit()
        new_chat = insert_res.scalars().first()
        return new_chat
    
    async def update_chat_by_uuid(
        self,
        chat_uuid: UUID,
        chat_data: ChatUpdate | ChatUpdatePartial,
        partial: bool = False,
    ) -> Chat:
        check_chat = await self.get_chat_by_uuid(chat_uuid=chat_uuid)
        chat_pydantic_update = ChatUpdatePartial if partial else ChatUpdate
        chat_pydantic_instance = chat_pydantic_update(**chat_data.model_dump())
        chat_dict = chat_pydantic_instance.model_dump(exclude_unset=partial)
        chat_model_instance = await self.session.get(Chat, chat_uuid)
        for key, value in chat_dict.items():
            setattr(chat_model_instance, key, value)
        await self.session.commit()
        await self.session.flush()
        await self.session.refresh(chat_model_instance)
        return chat_model_instance

    async def delete_chat_by_uuid(self, chat_uuid: UUID, soft: bool = False) -> UUID:
        check_chat = await self.get_chat_by_uuid(chat_uuid=chat_uuid)
        delete_stmt = update(Chat).where(Chat.uuid == chat_uuid).values(is_active=False, deleted_at=datetime.utcnow()).returning(Chat.uuid) if soft else delete(Chat).where(Chat.uuid == chat_uuid).returning(Chat.uuid)
        delete_res = self.session.execute(delete_stmt)
        await self.session.commit()
        return delete_res.scalars().first()
    