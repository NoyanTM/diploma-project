from enum import Enum
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str
    email: str
    password: str


class UserUpdate(BaseModel):
    password: str
    role: str
    is_active: bool


class UserUpdatePartial(BaseModel):
    name: str | None = None
    email: str | None = None
    password: str | None = None
    role: str | None = None
    is_active: bool | None = None


class UserRead(BaseModel):
    uuid: UUID
    name: str
    email: str
    is_active: bool
    role: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
