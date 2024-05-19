import uuid
from datetime import datetime
from typing import Annotated, Any, Annotated

from sqlalchemy import Null, String, DateTime, func, MetaData, JSON, Text
from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy.dialects.postgresql import JSONB, UUID

# Custom data types
intpk = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]
uuidpk = Annotated[uuid.UUID, mapped_column(UUID, primary_key=True, default=uuid.uuid4)]
jsonb = Annotated[dict[str, Any], mapped_column(JSONB)]
json = Annotated[dict[str, Any], mapped_column(JSON)]
text = Annotated[str, mapped_column(Text)]

str_512 = Annotated[str, 512]
str_256 = Annotated[str, 256]
str_128 = Annotated[str, 256]
str_64 = Annotated[str, 64]
str_32 = Annotated[str, 32]

created_at = Annotated[datetime, mapped_column(DateTime(timezone=True), server_default=func.now())]
updated_at = Annotated[datetime, mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())]
deleted_at = Annotated[datetime | None, mapped_column(DateTime(timezone=True), server_default=Null())]

# Optional - setting indexes naming accoring to specific DB convention
POSTGRES_INDEXES_NAMING_CONVENTION = {
    "ix": "%(column_0_label)s_idx",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}


# Collection for tables
class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=POSTGRES_INDEXES_NAMING_CONVENTION)

    type_annotation_map = {
        str_512: String(512),
        str_256: String(256),
        str_128: String(128),
        str_64: String(64),
        str_32: String(32),
    }
