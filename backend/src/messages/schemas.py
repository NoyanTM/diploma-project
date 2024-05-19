from typing import Any
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from src.schemas import str_positive


class MessageBase(BaseModel):
    content: str_positive # TODO: need to add message limit of symbols


class MessageCreate(MessageBase):
    pass    


class MessageUpdate(MessageBase):
    pass


class MessageUpdatePartial(BaseModel):
    content: str_positive | None = None


class MessageRead(MessageBase):
    model_config = ConfigDict(from_attributes=True)
    
    uuid: UUID
    chat_uuid: UUID
    is_active: bool
    additional_metadata: dict[Any, Any]
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
    