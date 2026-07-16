"""User Pydantic schemas — Identity domain."""

import uuid

from pydantic import EmailStr, Field

from shared.base_schema import AppBaseModel, EntitySchema


class UserCreateRequest(AppBaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=255)
    password: str = Field(min_length=12, max_length=128)


class UserUpdateRequest(AppBaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=255)


class UserResponse(EntitySchema):
    email: str
    full_name: str
    is_active: bool
    is_verified: bool


class TokenRequest(AppBaseModel):
    email: EmailStr
    password: str


class TokenResponse(AppBaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
