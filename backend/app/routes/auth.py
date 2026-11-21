from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr, Field

from app.core.dependencies import get_current_user
from app.services.auth_service import (
    auth_service,
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    AccountDisabledError,
    EmailVerificationRequiredError,
    AuthServiceError,
)
from app.services.verification_service import (
    CooldownActiveError,
    InvalidCodeError,
    MaxAttemptsExceededError,
    CodeExpiredOrNotFoundError,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# =====================================
# 1. REQUEST & RESPONSE SCHEMAS
# =====================================

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=2, max_length=150)
    role: Literal["candidate", "recruiter"]


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class VerifyEmailRequest(BaseModel):
    email: EmailStr
    code: str = Field(min_length=6, max_length=6)


class ResendVerificationRequest(BaseModel):
    email: EmailStr


# =====================================
# 2. REGISTER
# =====================================

@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
)
async def register(data: RegisterRequest):
    try:
        result = await auth_service.register_user(
            email=data.email,
            password=data.password,
            full_name=data.full_name,
            role=data.role,
        )
        return {
            "message": "Registration successful. Please verify your email with the 6-digit code sent.",
            "user": {
                "id": result["user_id"],
                "email": result["email"],
                "full_name": result["full_name"],
                "role": result["role"],
                "is_verified": False,
            },
            "email_sent": result["email_sent"],
        }
    except EmailAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )
    except AuthServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )


# =====================================
# 3. VERIFY EMAIL
# =====================================

@router.post("/verify-email")
def verify_email(data: VerifyEmailRequest):
    try:
        return auth_service.verify_email(email=data.email, code=data.code)
    except (CodeExpiredOrNotFoundError, InvalidCodeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except MaxAttemptsExceededError as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(exc),
        )
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


# =====================================
# 4. RESEND VERIFICATION CODE
# =====================================

@router.post("/resend-verification")
async def resend_verification(data: ResendVerificationRequest):
    try:
        return await auth_service.resend_verification_code(email=data.email)
    except CooldownActiveError as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(exc),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resend verification code",
        )


# =====================================
# 5. LOGIN
# =====================================

@router.post("/login")
def login(data: LoginRequest):
    try:
        return auth_service.authenticate_user(
            email=data.email,
            password=data.password,
        )
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    except AccountDisabledError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is disabled",
        )
    except EmailVerificationRequiredError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required.",
        )


# =====================================
# 6. GET CURRENT AUTHENTICATED USER
# =====================================

@router.get("/me")
def get_me(
    current_user: dict = Depends(get_current_user),
):
    return {
        "user": current_user,
    }
