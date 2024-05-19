from uuid import UUID
from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import func, select, insert, delete, update, asc, desc
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.users import User
from src.auth.password import ArgonPasswordHashing
from src.pagination import OrderEnum, PageParams
from src.users.schemas import (
    UserCreate,
    UserCreateDB,
    UserFilterParams,
    UserUpdate,
    UserUpdateDB,
    UserUpdatePartial,
    UserUpdatePartialDB,
    UserRead,
)
from src.users.exceptions import (
    UserNotFoundException,
    InactiveUserException,
    InvalidCredentialsException,
    UserAlreadyExistsException,
)

class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_user_by_uuid(self, user_uuid: UUID) -> User:
        select_stmt = select(User).where(User.uuid == user_uuid)
        select_res = await self.session.execute(select_stmt)
        user = select_res.scalar_one_or_none()
        if user is None:
            raise UserNotFoundException
        return user
    
    async def get_user_by_email(self, user_email: str) -> User:
        select_stmt = select(User).where(User.email == user_email)
        select_res = await self.session.execute(select_stmt)
        user = select_res.scalar_one_or_none()
        if user is None:
            raise UserNotFoundException
        return user
    
    async def get_users(
        self,
        pagination_params: PageParams,
        filter_params: UserFilterParams | None = None,
    ) -> list[UserRead] | None:
        select_stmt = (
            select(User)
            .where(
                User.role == filter_params.role if filter_params.role else True,
                User.is_active == filter_params.is_active if filter_params.is_active else True,
            )
            .order_by(
                asc(User.created_at)
                if pagination_params.order is OrderEnum.ASC
                else desc(User.created_at)
            )
            .limit(pagination_params.size)
            .offset(
                pagination_params.page - 1
                if pagination_params.page == 1
                else (pagination_params.page - 1) * pagination_params.size
            )
        )
        select_res = await self.session.execute(select_stmt)
        users_models = select_res.scalars().all()
        users_schemas = [UserRead.model_validate(users_model) for users_model in users_models]
        return users_schemas
    
    async def count_users(
        self,
        filter_params: UserFilterParams | None = None,
    ) -> int | None:
        select_stmt = (
            select(func.count())
            .select_from(User)
            .where(
                User.role == filter_params.role if filter_params.role else True,
                User.is_active == filter_params.is_active if filter_params.is_active else True,
            )
        )
        select_res = await self.session.execute(select_stmt)
        count = select_res.scalar()
        return count
    
    async def create_user(self, user_data: UserCreate) -> User: # BaseModel
        select_stmt = select(User).where(User.email == user_data.email)
        select_res = await self.session.execute(select_stmt)
        user = select_res.scalar_one_or_none()
        if user:
            raise UserAlreadyExistsException
        hashed_password = ArgonPasswordHashing.hash_password(user_data.password)
        user_pydantic_model = UserCreateDB(
            **user_data.model_dump(),
            hashed_password=hashed_password,
        )
        user_dict = user_pydantic_model.model_dump()
        insert_stmt = insert(User).values(**user_dict).returning(User)
        insert_res = await self.session.execute(insert_stmt)
        await self.session.commit()
        new_user = insert_res.scalars().first()
        return new_user
        
    async def update_user_by_uuid(
        self,
        user_uuid: UUID,
        user_data: UserUpdate | UserUpdatePartial,
        partial: bool = False,
    ) -> User:
        check_user = await self.get_user_by_uuid(user_uuid=user_uuid)
        user_pydantic_update = UserUpdatePartialDB if partial else UserUpdateDB
        
        if user_data.email:
            select_stmt = select(User).where(User.email == user_data.email)
            select_res = await self.session.execute(select_stmt)
            check_email = select_res.scalar_one_or_none()
            if check_email and check_email.uuid != user_uuid:
                raise UserAlreadyExistsException

        if user_data.password:
            hashed_password = ArgonPasswordHashing.hash_password(user_data.password)
            user_pydantic_model = user_pydantic_update(
                **user_data.model_dump(),
                hashed_password=hashed_password,
            )

        if not user_data.password:
            user_pydantic_model = user_pydantic_update(**user_data.model_dump())

        user_dict = user_pydantic_model.model_dump(exclude_unset=partial, exclude_none=partial)
        user_model_instance = await self.session.get(User, user_uuid)
        for key, value in user_dict.items():
            setattr(user_model_instance, key, value)
        await self.session.commit()
        await self.session.flush()
        await self.session.refresh(user_model_instance)
        return user_model_instance
    
    async def delete_user_by_uuid(self, user_uuid: UUID, soft: bool = False) -> UUID:
        check_user = await self.get_user_by_uuid(user_uuid=user_uuid)
        delete_stmt = update(User).where(User.uuid == user_uuid).values(is_active=False, deleted_at=datetime.utcnow()).returning(User.uuid) if soft else delete(User).where(User.uuid == user_uuid).returning(User.uuid)
        delete_res = await self.session.execute(delete_stmt)
        await self.session.commit()
        return delete_res.scalars().first()

    async def delete_user_by_email(self, user_email: str, soft: bool = False) -> str:
        check_user = await self.get_user_by_email(user_email=user_email)
        delete_stmt = update(User).where(User.email == user_email).values(is_active=False, deleted_at=datetime.utcnow()).returning(User.email) if soft else delete(User).where(User.email == user_email).returning(User.email)
        delete_res = self.session.execute(delete_stmt)
        await self.session.commit()
        return delete_res.scalars().first()
