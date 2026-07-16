"""
JWT Service — issues and validates access/refresh tokens.

Uses python-jose for encoding/decoding and passlib for password hashing.
All configuration comes from the Enterprise Configuration System.
"""

import uuid
from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import SecretStr

from app.config import get_settings
from app.platform.auth.models import TokenPair, TokenPayload
from app.platform.logging import get_logger

logger = get_logger(__name__)

_pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


class JWTService:
    def __init__(self) -> None:
        self._settings = get_settings()

    def create_token_pair(
        self, user_id: uuid.UUID, email: str, roles: list[str]
    ) -> TokenPair:
        now = datetime.now(UTC)
        jti = str(uuid.uuid4())

        access = self._encode(
            sub=str(user_id), email=email, roles=roles, jti=jti,
            exp=now + timedelta(minutes=self._settings.jwt.access_token_expire_minutes),
            kind="access",
        )
        refresh = self._encode(
            sub=str(user_id), email=email, roles=roles, jti=str(uuid.uuid4()),
            exp=now + timedelta(days=self._settings.jwt.refresh_token_expire_days),
            kind="refresh",
        )
        return TokenPair(
            access_token=access,
            refresh_token=refresh,
            expires_in=self._settings.jwt.access_token_expire_minutes * 60,
        )

    def decode_access_token(self, token: str) -> TokenPayload | None:
        try:
            data = jwt.decode(
                token, self._get_secret(self._settings.jwt.secret_key),
                algorithms=[self._settings.jwt.algorithm],
            )
            if data.get("kind") != "access":
                return None
            return TokenPayload(
                sub=data["sub"], email=data["email"], roles=data["roles"],
                jti=data["jti"], exp=datetime.fromtimestamp(data["exp"], UTC),
                iat=datetime.fromtimestamp(data["iat"], UTC),
            )
        except JWTError as exc:
            logger.warning("jwt_decode_failed", error=str(exc))
            return None

    def hash_password(self, password: str) -> str:
        return _pwd_ctx.hash(password)

    def verify_password(self, plain: str, hashed: str) -> bool:
        return _pwd_ctx.verify(plain, hashed)

    @staticmethod
    def _get_secret(key: SecretStr | str) -> str:
        return key.get_secret_value() if isinstance(key, SecretStr) else key

    def _encode(
        self, sub: str, email: str, roles: list[str],
        jti: str, exp: datetime, kind: str,
    ) -> str:
        now = datetime.now(UTC)
        return jwt.encode(
            {"sub": sub, "email": email, "roles": roles, "jti": jti,
             "exp": exp, "iat": now, "kind": kind},
            self._get_secret(self._settings.jwt.secret_key),
            algorithm=self._settings.jwt.algorithm,
        )


def get_jwt_service() -> JWTService:
    return JWTService()
