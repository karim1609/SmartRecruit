
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from bson import ObjectId
from bson.errors import InvalidId
import jwt

from app.database.connection import users_collection
from app.core.security import decode_access_token


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")

        if not user_id:
            raise credentials_exception

        user = users_collection.find_one(
            {"_id": ObjectId(user_id)}
        )

        if not user or not user.get("is_active", True):
            raise credentials_exception

        return {
            "id": str(user["_id"]),
            "email": user["email"],
            "role": user["role"]
        }

    except (jwt.InvalidTokenError, InvalidId, TypeError):
        raise credentials_exception
def require_role(*allowed_roles: str):

    def role_checker(
        current_user: dict = Depends(get_current_user)
    ):
        if current_user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this resource"
            )

        return current_user

    return role_checker