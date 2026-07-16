"""Authentication dependencies — FastAPI dependency injection for JWT validation."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.platform.auth.jwt import JWTService, TokenPayload, get_jwt_service

_bearer = HTTPBearer(auto_error=True)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer)],
    jwt_service: Annotated[JWTService, Depends(get_jwt_service)],
) -> TokenPayload:
    """
    Decodes and validates the JWT bearer token.
    Raises HTTP 401 if missing or invalid.

    Usage:
        async def endpoint(user: TokenPayload = Depends(get_current_user)): ...
    """
    payload = jwt_service.decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload


CurrentUser = Annotated[TokenPayload, Depends(get_current_user)]
