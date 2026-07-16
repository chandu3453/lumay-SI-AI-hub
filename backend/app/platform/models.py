"""
Authentication Domain Models.

Pydantic models for JWT token payloads and auth-related data structures.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class TokenPayload(BaseModel):
    """Decoded JWT access token payload."""

    sub: str = Field(description="Subject — user UUID string")
    email: str
    roles: list[str] = Field(default_factory=list)
    iat: datetime
    exp: datetime
    jti: str = Field(description="JWT ID — unique token identifier for revocation")

    @property
    def user_id(self) -> uuid.UUID:
        return uuid.UUID(self.sub)

    def has_role(self, role: str) -> bool:
        return role in self.roles


class TokenPair(BaseModel):
    """Issued JWT token pair returned on successful authentication."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="Access token TTL in seconds")
