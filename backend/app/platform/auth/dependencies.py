from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.platform.auth.models import TokenPayload
from app.platform.jwt import JWTService, get_jwt_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

CurrentUser = TokenPayload


async def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    jwt_service: JWTService = Depends(get_jwt_service),
) -> CurrentUser | None:
    if token is None:
        return None
    payload = jwt_service.decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    return payload


async def get_current_active_user(
    current_user: CurrentUser | None = Depends(get_current_user),
) -> CurrentUser:
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    return current_user
