
from pydantic import BaseModel, EmailStr, Field
from typing import Literal
from datetime import datetime, timezone


# Roles available in SmartRecruit
UserRole = Literal["candidate", "recruiter", "admin"]


# Data received when a user registers
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    role: Literal["candidate", "recruiter"]


# User representation stored in MongoDB
class UserInDB(BaseModel):
    email: EmailStr
    hashed_password: str
    full_name: str
    role: UserRole
    is_active: bool = True
    is_verified: bool = False
    email_verified_at: datetime | None = None
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

# Data returned to the frontend
class UserResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: str | None = None
    role: UserRole
    is_active: bool
    is_verified: bool = False
    email_verified_at: datetime | None = None
    created_at: datetime
