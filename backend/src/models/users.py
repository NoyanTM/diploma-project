from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import (
    Base,
    uuidpk,
    str_128,
    created_at,
    updated_at,
    deleted_at,
    text
)

if TYPE_CHECKING:
    from src.models.chats import Chat


class Role(str, Enum):
    USER = "USER"
    MODERATOR = "MODERATOR"
    ADMIN = "ADMIN"


class User(Base):
    __tablename__ = "user"

    uuid: Mapped[uuidpk]
    name: Mapped[str_128]
    email: Mapped[str_128] = mapped_column(unique=True)
    hashed_password: Mapped[str_128]
    role: Mapped["Role"] = mapped_column(default=Role.USER)
    photo_url: Mapped[text | None] # TODO: need minio or other s3 bucket
    is_active: Mapped[bool] = mapped_column(default=True) # TODO: soft-delete / deactivation status
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
    deleted_at: Mapped[deleted_at] # TODO: soft-delete / deactivate datetime - need to make business logic for that
    
    chat: Mapped[list["Chat"]] = relationship(back_populates="user")
    
    def __repr__(self):
        return f"User(uuid={self.uuid}, name={self.name}, email={self.email})"
