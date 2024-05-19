from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator

from src.models.users import Role
from src.auth.password import PasswordValidation
from src.schemas import str_128, email_str, int_positive


class UserValidationMixin:
    @field_validator("password", mode="after")
    @classmethod
    def validate_password(cls, value: str) -> str:
        errors = []
        if not PasswordValidation.verify_password_pattern(value):
            errors.append(
                "хотя бы c одной строчной буквой, "
                "хотя бы c одной заглавной буквой, "
                "хотя бы c одной цифрой, "
                "хотя бы c одним специальным символом (!@#$%^&*), "
                "длинной от 12 до 128 символов, "
            )
        if not PasswordValidation.verify_password_entropy(value):
            errors.append("из бессмысленного или хаотичного набора символов")
        if errors:
            raise ValueError("Пароль должен быть " + ", ".join(errors))
        return value


class UserBase(BaseModel):
    name: str_128
    email: email_str


class UserCreate(UserBase, UserValidationMixin):
    password: str_128


class UserCreateDB(UserBase):
    hashed_password: str_128


class UserUpdate(UserBase, UserValidationMixin):
    password: str_128
    role: Role
    is_active: bool


class UserUpdateDB(UserBase):
    hashed_password: str_128
    role: Role
    is_active: bool


class UserUpdatePartial(BaseModel, UserValidationMixin):
    name: str_128 | None = None
    email: email_str | None = None
    password: str_128 | None = None
    role: Role | None = None
    is_active: bool | None = None


class UserUpdatePartialDB(BaseModel):
    name: str_128 | None = None
    email: email_str | None = None
    hashed_password: str_128 | None = None
    role: Role | None = None
    is_active: bool | None = None


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    uuid: UUID
    # hashed_password: str
    is_active: bool
    role: Role
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None


class UserFilterParams(BaseModel):
    role: Role | None = None
    is_active: bool | None = None
    