from uuid import UUID
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import (
    Base,
    uuidpk,
    text,
    jsonb,
    created_at,
    updated_at,
    deleted_at,
)

if TYPE_CHECKING:
    from src.models.chats import Chat


class Message(Base):
    __tablename__ = "message"

    uuid: Mapped[uuidpk]
    content: Mapped[text]
    additional_metadata: Mapped[jsonb | None] # TODO: metadata or something add message tag (user / system) in order to understand which one is and what operation was or other params here
    is_active: Mapped[bool] = mapped_column(default=True) # TODO: soft-delete / deactivation status
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
    deleted_at: Mapped[deleted_at] # TODO: soft-delete / deactivate datetime - need to make business logic for that

    chat_uuid: Mapped[UUID | None] = mapped_column(ForeignKey("chat.uuid")) # TODO: delete "| None" because message must be within specific chat
    chat: Mapped["Chat"] = relationship(back_populates="message")

    def __repr__(self):
        return f"Message(uuid={self.uuid}, content={self.content})"
