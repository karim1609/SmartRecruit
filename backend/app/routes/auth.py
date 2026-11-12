
from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr, Field
from pymongo.errors import DuplicateKeyError

from app.database.connection import (
    users_collection,
    candidates_collection,
    recruiters_collection
)

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)

from app.core.dependencies import get_current_user


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# =====================================
# 1. REQUEST SCHEMAS
# =====================================

class RegisterRequest(BaseModel):

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128
    )

    full_name: str = Field(
        min_length=2,
        max_length=150
    )

    role: Literal["candidate", "recruiter"]


class LoginRequest(BaseModel):

    email: EmailStr

    password: str


# =====================================
# 2. REGISTER
# =====================================

@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED
)
def register(data: RegisterRequest):

    # Normalize email
    email = str(data.email).lower()

    # Check if email already exists
    existing_user = users_collection.find_one({
        "email": email
    })

    if existing_user:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Create user document
    user_document = {
        "email": email,
        "hashed_password": hash_password(data.password),
        "full_name": data.full_name,
        "role": data.role,
        "is_active": True,
        "created_at": datetime.now(timezone.utc)
    }

    result = None

    try:

        # Insert user into users collection
        result = users_collection.insert_one(user_document)

        user_id = str(result.inserted_id)

        # Common profile fields
        profile_document = {
            "user_id": user_id,
            "full_name": data.full_name,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }

        # Create candidate profile
        if data.role == "candidate":

            profile_document.update({
                "skills": [],
                "education": [],
                "experience": []
            })

            candidates_collection.insert_one(profile_document)

        # Create recruiter profile
        elif data.role == "recruiter":

            profile_document.update({
                "phone": None,
                "job_title": None,
                "company_id": None
            })

            recruiters_collection.insert_one(profile_document)

    except DuplicateKeyError:

        # Clean up if user was already inserted
        if result is not None:

            candidates_collection.delete_one({
                "user_id": str(result.inserted_id)
            })

            recruiters_collection.delete_one({
                "user_id": str(result.inserted_id)
            })

            users_collection.delete_one({
                "_id": result.inserted_id
            })

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email or profile already exists"
        )

    except Exception:

        # Compensating cleanup if profile creation fails
        if result is not None:

            user_id = str(result.inserted_id)

            candidates_collection.delete_one({
                "user_id": user_id
            })

            recruiters_collection.delete_one({
                "user_id": user_id
            })

            users_collection.delete_one({
                "_id": result.inserted_id
            })

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not complete registration"
        )

    # Registration response
    return {
        "message": "Registration successful",

        "user": {
            "id": user_id,
            "email": email,
            "full_name": data.full_name,
            "role": data.role
        }
    }


# =====================================
# 3. LOGIN
# =====================================

@router.post("/login")
def login(data: LoginRequest):

    # Normalize email
    email = str(data.email).lower()

    # Find user
    user = users_collection.find_one({
        "email": email
    })

    # Verify email and password
    if not user or not verify_password(
        data.password,
        user["hashed_password"]
    ):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Check account status
    if not user.get("is_active", True):

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is disabled"
        )

    # Generate JWT access token
    access_token = create_access_token(
        user_id=str(user["_id"])
    )

    # Return authentication response
    return {
        "access_token": access_token,
        "token_type": "bearer",

        "user": {
            "id": str(user["_id"]),
            "email": user["email"],
            "full_name": user.get("full_name"),
            "role": user["role"]
        }
    }


# =====================================
# 4. GET CURRENT AUTHENTICATED USER
# =====================================

@router.get("/me")
def get_me(
    current_user: dict = Depends(get_current_user)
):

    return {
        "user": current_user
    }
