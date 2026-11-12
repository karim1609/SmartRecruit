
from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict

from app.database.connection import users_collection
from app.core.dependencies import get_current_user, require_role


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# ==========================================
# RESPONSE SCHEMA
# ==========================================

class UserResponse(BaseModel):
    id: str
    email: str
    role: str
    is_active: bool
    created_at: datetime


# ==========================================
# UPDATE STATUS SCHEMA
# ==========================================

class UserStatusUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_active: bool


# ==========================================
# GET ALL USERS (ADMIN ONLY)
# ==========================================

@router.get("/", response_model=list[UserResponse])
def get_all_users(
    current_user: dict = Depends(require_role("admin")),
    skip: int = 0,
    limit: int = 20
):
    if skip < 0 or limit < 1 or limit > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid pagination parameters"
        )

    users = users_collection.find(
        {},
        {
            "hashed_password": 0
        }
    ).skip(skip).limit(limit)

    return [
        {
            "id": str(user["_id"]),
            "email": user["email"],
            "role": user["role"],
            "is_active": user.get("is_active", True),
            "created_at": user["created_at"]
        }
        for user in users
    ]


# ==========================================
# GET USER BY ID (ADMIN ONLY)
# ==========================================

@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(
    user_id: str,
    current_user: dict = Depends(require_role("admin"))
):
    try:
        object_id = ObjectId(user_id)
    except (InvalidId, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID"
        )

    user = users_collection.find_one(
        {"_id": object_id},
        {"hashed_password": 0}
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return {
        "id": str(user["_id"]),
        "email": user["email"],
        "role": user["role"],
        "is_active": user.get("is_active", True),
        "created_at": user["created_at"]
    }


# ==========================================
# ACTIVATE / DEACTIVATE USER (ADMIN ONLY)
# ==========================================

@router.patch("/{user_id}/status", response_model=UserResponse)
def update_user_status(
    user_id: str,
    data: UserStatusUpdate,
    current_user: dict = Depends(require_role("admin"))
):
    try:
        object_id = ObjectId(user_id)
    except (InvalidId, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID"
        )

    # Prevent an administrator from deactivating themselves
    if str(object_id) == current_user["id"] and data.is_active is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot deactivate your own account"
        )

    result = users_collection.update_one(
        {"_id": object_id},
        {
            "$set": {
                "is_active": data.is_active,
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user = users_collection.find_one(
        {"_id": object_id},
        {"hashed_password": 0}
    )

    return {
        "id": str(user["_id"]),
        "email": user["email"],
        "role": user["role"],
        "is_active": user["is_active"],
        "created_at": user["created_at"]
    }
