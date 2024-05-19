import re
import math
import string

from argon2 import PasswordHasher
from argon2.exceptions import (
    HashingError,
    VerifyMismatchError,
    VerificationError,
    InvalidHashError,
)

from src.config import settings


class ArgonPasswordHashing:
    ph = PasswordHasher(
        salt_len=settings.ARGON_SALT_LEN,
        hash_len=settings.ARGON_HASH_LEN,
        time_cost=settings.ARGON_TIME_COST,
        memory_cost=settings.ARGON_MEMORY_COST,
        parallelism=settings.ARGON_PARALLELISM,
    )

    @classmethod
    def hash_password(cls, password: str) -> str:
        try:
            return cls.ph.hash(password)
        except HashingError:
            return None

    @classmethod
    def verify_password(cls, password: str, hashed_password: str) -> bool:
        try:
            return cls.ph.verify(hashed_password, password)
        except (VerifyMismatchError, VerificationError):
            return False

    @classmethod
    def verify_password_rehash(cls, hashed_password: str) -> bool:
        try:
            return cls.ph.check_needs_rehash(hashed_password)
        except InvalidHashError:
            return False


class PasswordValidation:
    ASCII_LIMITED_CHARACTERS = string.ascii_uppercase + string.ascii_lowercase + string.digits + string.punctuation
    REGEX_PASSWORD_PATTERN = re.compile(r"^(?=.*[\d])(?=.*[A-Z])(?=.*[a-z])(?=.*[!@#$%^&*])[A-Za-z0-9!@#$%^&*]{12,128}$")
    PASSWORD_ENTROPY_POINTS = 32
    
    @classmethod
    def verify_password_entropy(cls, password: str, option: bool = False) -> int:
        unique_characters = cls.ASCII_LIMITED_CHARACTERS if option else set(password)
        entropy_bits = round(math.log2(len(unique_characters) ** len(password)))
        return True if entropy_bits > cls.PASSWORD_ENTROPY_POINTS else False

    @classmethod
    def verify_password_pattern(cls, password: str):
        return re.match(cls.REGEX_PASSWORD_PATTERN, password)
