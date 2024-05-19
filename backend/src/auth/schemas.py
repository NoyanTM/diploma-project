from pydantic import BaseModel

from src.schemas import email_str, str_128
from src.users.schemas import UserValidationMixin

class TokenData(BaseModel):
    username: str | None = None


class UserAuth(BaseModel, UserValidationMixin):
    email: email_str
    password: str_128


class Token(BaseModel):
    access_token: str
    # refresh_token: str
    token_type: str


# class RefreshSessionCreate(BaseModel):
#     refresh_token: uuid.UUID
#     expires_in: int
#     user_id: uuid.UUID


# class RefreshSessionUpdate(RefreshSessionCreate):
#     user_id: uuid.UUID | None = Field(None)
