from uuid import UUID
from datetime import datetime

from pydantic import BaseModel

from src.schemas.messages import MessageRead


class ChatBase(BaseModel):
    title: str | None
    description: str | None


class ChatCreate(BaseModel):
    title: str | None
    description: str | None


class ChatUpdate(BaseModel):
    title: str | None
    description: str | None


class ChatUpdatePartial(BaseModel):
    title: str | None = None
    description: str | None = None


class ChatRead(ChatBase):
    uuid: UUID
    user_uuid: UUID # user: UserRead 
    created_at: datetime
    updated_at: datetime


class ChatMessageRead(ChatRead):
    messages: list["MessageRead"] = []


class ChatFilterParams(BaseModel):
    is_active: bool | None = None
