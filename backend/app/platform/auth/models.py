import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class TokenPayload:
    sub: str
    email: str
    roles: list[str]
    jti: str
    exp: datetime
    iat: datetime

    @property
    def user_id(self) -> uuid.UUID:
        return uuid.UUID(self.sub)

    def has_role(self, role: str) -> bool:
        return role in self.roles


@dataclass(frozen=True)
class TokenPair:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 1800
