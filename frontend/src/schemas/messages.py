from typing import Any
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel


class MessageCreate(BaseModel):
    content: str 


class MessageUpdate(BaseModel):
    content: str 


class MessageUpdatePartial(BaseModel):
    content: str | None = None


class MessageRead(BaseModel):
    uuid: UUID
    chat_uuid: UUID
    content: str
    additional_metadata: dict[Any, Any]
    created_at: datetime
    updated_at: datetime
    