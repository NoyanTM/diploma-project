from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from src.schemas import str_positive
from src.messages.schemas import MessageRead


class ChatBase(BaseModel):
    title: str | None # str_positive
    description: str | None # str_positive


class ChatCreate(BaseModel):
    pass


class ChatUpdate(BaseModel):
    pass


class ChatUpdatePartial(BaseModel):
    title: str | None = None # str_positive
    description: str | None = None # str_positive


class ChatRead(ChatBase):
    model_config = ConfigDict(from_attributes=True)
    
    uuid: UUID
    user_uuid: UUID # user: UserRead 
    is_active: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None


class ChatMessageRead(ChatRead):
    message: list[MessageRead] = [] # "MessageRead"


class ChatFilterParams(BaseModel):
    is_active: bool | None = None


# class QueryType(str, Enum):


class Document(BaseModel):
    page_content: str = Field(exclude=True) # page_content: str
    metadata: dict = Field(default_factory=dict)
