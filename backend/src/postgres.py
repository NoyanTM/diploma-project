from typing import Annotated, AsyncGenerator, Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from src.config import settings
from src.exceptions import DatabaseException

# Engine connection configuration, use "echo=True" only when debugging application (not in prduction)
engine = create_async_engine(url=f"{settings.POSTGRES_URL}", echo=True)

# For session factory in everywhere "async with async_session_maker() as session:"
async_session_maker = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

# For dependency injection in only routers usually "Depends(get_async_session)"
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
        except SQLAlchemyError as e:
            print("Database exception:", e)
            await session.rollback()
            raise DatabaseException
        finally:
            await session.close()

# Optional short passing async session via annotated even instead of "session: AsyncSession = Depends(get_async_session)"
AsyncDep = Annotated[AsyncSession, Depends(get_async_session)]
