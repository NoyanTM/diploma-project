from uuid import UUID
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import (
    Base,
    uuidpk,
    str_128,
    str_512,
    created_at,
    updated_at,
    deleted_at,
)

if TYPE_CHECKING:
    from src.models.users import User
    from src.models.messages import Message


class Chat(Base):
    __tablename__ = "chat"

    uuid: Mapped[uuidpk]
    title: Mapped[str_128 | None] # TODO: title can be: generated by llm so it is a short summary of conversation like in chatgpt app, or it can be edited by user itself
    is_active: Mapped[bool] = mapped_column(default=True) # TODO: soft-delete / deactivation status
    description: Mapped[str_512 | None] # TODO: description like medium context summary, but maybe it must be as seperate another table for this case
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
    deleted_at: Mapped[deleted_at] # TODO: soft-delete / deactivate datetime - need to make business logic for that

    user_uuid: Mapped[UUID] = mapped_column(ForeignKey("user.uuid"))
    user: Mapped["User"] = relationship(back_populates="chat")
    
    message: Mapped[list["Message"]] = relationship(back_populates="chat")

    def __repr__(self):
        return f"Chat(uuid={self.uuid}, title={self.title})"
