from src.auth.password import ArgonPasswordHashing
from src.auth.jwt import JWT
from src.models.users import User
from src.users.services import UserService
from src.postgres import AsyncDep
from src.auth.schemas import Token, TokenData, UserAuth
from src.config import settings
from src.auth.exceptions import (
    InvalidCredentialsException,
    InactiveUserException,
)

class AuthService:
    def __init__(self, session: AsyncDep):
        self.user_repo = UserService(session)
    
    async def _authenticate_user(self, user_email: str, user_password: str) -> User:
        user = await self.user_repo.get_user_by_email(user_email=user_email)
        if not (user and ArgonPasswordHashing.verify_password(user_password, user.hashed_password)):
            raise InvalidCredentialsException
        if not user.is_active: # TODO: optional here, maybe delete
            raise InactiveUserException
        # if ArgonPasswordHashing.verify_password_rehash(user.hashed_password): # TODO: password rehashing if configuration of argon changed
        #     new_hashed_password = ArgonPasswordHashing.hash_password(user_password)
        #     await self.user_repo.update_user_by_email(user_email / identifier = user_data.email, hashed_password=new_hashed_password)
        return user

    async def generate_token(self, user_email: str, user_password: str) -> Token:
        user = await self._authenticate_user(user_email=user_email, user_password=user_password)
        access_token = JWT.encode_jwt(
            secret_key = settings.ACCESS_SECRET_KEY,
            data={
                "sub": user.email,
                "role": user.role,
            },
        )
        # refresh_token = JWT.encode_jwt(
        #     secret_key = settings.ACCESS_SECRET_KEY,
        #     data={
        #         "sub": user.email,
        #         "role": user.role,
        #     },
        #     expire_seconds = settings.REFRESH_SECRET_KEY
        # )
        return Token(
            access_token=access_token,
            # refresh_token=refresh_token,
            token_type="bearer"
        )
        
    # async def refresh_token():
    # async def block_token():
    # user_data: UserAuth, form_data: OAuth2PasswordRequestForm
    # form_data.username, form_data.password
    