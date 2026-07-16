import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr

from app.platform.auth.dependencies import get_current_user
from app.platform.auth.models import TokenPair, TokenPayload
from app.platform.jwt import JWTService, get_jwt_service
from app.platform.logging import get_logger
from shared.response_schemas import SuccessResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = get_logger(__name__)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


DEMO_EMAIL = "admin@gmail.com"
DEMO_PASSWORD = "Admin@123"


@router.post("/login")
async def login(
    body: LoginRequest,
    jwt_service: JWTService = Depends(get_jwt_service),
) -> SuccessResponse[TokenPair]:
    if body.email != DEMO_EMAIL or body.password != DEMO_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password. Please try again.",
        )
    tokens = jwt_service.create_token_pair(
        user_id=uuid.uuid4(),
        email=body.email,
        roles=["admin", "agent", "manager"],
    )
    logger.info("demo_login", email=body.email)
    return SuccessResponse(data=tokens)


@router.get("/me")
async def me(
    current_user: TokenPayload | None = Depends(get_current_user),
) -> SuccessResponse[dict]:
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return SuccessResponse(data={
        "id": str(current_user.sub),
        "email": current_user.email,
        "full_name": current_user.email.split("@")[0].replace(".", " ").title(),
        "roles": current_user.roles,
    })
