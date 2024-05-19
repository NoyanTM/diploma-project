from typing import Any

from dotenv import find_dotenv, load_dotenv
from pydantic import PostgresDsn, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Locate .env file for pydantic, because pydantic_settings only checks
# current working dir and cannot check any parent directories for .env file
load_dotenv(find_dotenv(".env"))


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="allow")

    # 1. Postgres Database Configs:
    POSTGRES_PREFIX: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_URL: PostgresDsn | None = None

    @field_validator("POSTGRES_URL", mode="before")
    @classmethod
    def assemble_postgres_url(cls, value: str | None, values: ValidationInfo) -> Any:
        if isinstance(value, str):
            return value
        return PostgresDsn.build(
            scheme=values.data.get("POSTGRES_PREFIX"),
            username=values.data.get("POSTGRES_USER"),
            password=values.data.get("POSTGRES_PASSWORD"),
            host=values.data.get("POSTGRES_HOST"),
            port=values.data.get("POSTGRES_PORT"),
            path=f"{values.data.get('POSTGRES_DB') or ''}",
        )

    # 2. CORS Configs (for frontend):
    ALLOWED_CORS_ORIGINS: list[str]
    ALLOWED_CORS_METHODS: list[str]
    ALLOWED_CORS_HEADERS: list[str]
    
    # 3. JWT Configs (only symmetric algorithms):
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_SECONDS: int
    REFRESH_TOKEN_EXPIRE_SECONDS: int
    ACCESS_SECRET_KEY: str
    REFRESH_SECRET_KEY: str
    
    # 4. Password Hashing Configs (for argon2id):
    ARGON_SALT_LEN: int
    ARGON_HASH_LEN: int
    ARGON_TIME_COST: int
    ARGON_MEMORY_COST: int
    ARGON_PARALLELISM: int
    
    # 5. Langfuse Configs (for debug):
    LANGFUSE_SECRET_KEY: str
    LANGFUSE_PUBLIC_KEY: str
    LANGFUSE_HOST: str
    
    
settings = Settings()
