from datetime import datetime, timedelta, timezone

import jwt

from src.config import settings


class JWT:
    def encode_jwt(
        data: dict,
        secret_key: str,
        algorithm: str = settings.JWT_ALGORITHM,
        expire_seconds: int = settings.ACCESS_TOKEN_EXPIRE_SECONDS,
        expire_timedelta: timedelta | None = None,
    ) -> str:
        payload = data.copy()
        now = datetime.now(timezone.utc)
        if expire_timedelta:
            expire = now + expire_timedelta
        else:
            expire = now + timedelta(seconds=expire_seconds)
        payload.update(
            exp=expire,
            iat=now,
        )
        encoded_jwt = jwt.encode(
            payload=payload,
            key=secret_key,
            algorithm=algorithm,
        )
        return encoded_jwt

    def decode_jwt(
        token: str | bytes,
        secret_key: str,
        algorithm: str = settings.JWT_ALGORITHM,
        # audience: List[str]
    ) -> dict: # Dict[str, Any]
        decoded_jwt = jwt.decode(
            jwt=token,
            key=secret_key,
            algorithms=[algorithm],
            # audience=audience
        )
        return decoded_jwt
