import logging
from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from app.database.connection import (
    users_collection,
    candidates_collection,
    recruiters_collection,
)
from app.core.security import hash_password, verify_password, create_access_token
from app.services.verification_service import (
    verification_service,
    CooldownActiveError,
    InvalidCodeError,
    MaxAttemptsExceededError,
    CodeExpiredOrNotFoundError,
)
from app.services.email_service import email_service, EmailServiceError

logger = logging.getLogger(__name__)


class AuthServiceError(Exception):
    """Base exception for auth service."""
    pass


class EmailAlreadyExistsError(AuthServiceError):
    pass


class InvalidCredentialsError(AuthServiceError):
    pass


class AccountDisabledError(AuthServiceError):
    pass


class EmailVerificationRequiredError(AuthServiceError):
    pass


class AuthService:
    """Handles authentication, registration workflow, verification, and token issuance."""

    async def register_user(
        self,
        email: str,
        password: str,
        full_name: str,
        role: str,
    ) -> dict[str, Any]:
        """Register user, create profile, issue verification code, and send verification email."""
        normalized_email = email.lower().strip()

        # Check existing user
        if users_collection.find_one({"email": normalized_email}):
            raise EmailAlreadyExistsError("Email already registered")

        user_document = {
            "email": normalized_email,
            "hashed_password": hash_password(password),
            "full_name": full_name,
            "role": role,
            "is_active": True,
            "is_verified": False,
            "email_verified_at": None,
            "created_at": datetime.now(timezone.utc),
        }

        result = None
        try:
            result = users_collection.insert_one(user_document)
            user_id = str(result.inserted_id)

            profile_document = {
                "user_id": user_id,
                "full_name": full_name,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            }

            if role == "candidate":
                profile_document.update({
                    "skills": [],
                    "education": [],
                    "experience": [],
                })
                candidates_collection.insert_one(profile_document)
            elif role == "recruiter":
                profile_document.update({
                    "phone": None,
                    "job_title": None,
                    "company_id": None,
                })
                recruiters_collection.insert_one(profile_document)

        except DuplicateKeyError as exc:
            if result is not None:
                candidates_collection.delete_one({"user_id": str(result.inserted_id)})
                recruiters_collection.delete_one({"user_id": str(result.inserted_id)})
                users_collection.delete_one({"_id": result.inserted_id})
            raise EmailAlreadyExistsError("Email or profile already exists") from exc
        except Exception as exc:
            if result is not None:
                candidates_collection.delete_one({"user_id": str(result.inserted_id)})
                recruiters_collection.delete_one({"user_id": str(result.inserted_id)})
                users_collection.delete_one({"_id": result.inserted_id})
            logger.error("Registration failed for %s: %s", normalized_email, exc)
            raise AuthServiceError("Could not complete registration") from exc

        # Generate verification code and store in Redis
        code = verification_service.create_verification_code(normalized_email, force_ignore_cooldown=True)

        # Attempt sending verification email
        email_sent = True
        try:
            await email_service.send_verification_email(
                to_email=normalized_email,
                full_name=full_name,
                code=code,
            )
        except Exception as exc:
            logger.error("Failed to send verification email during registration to %s: %s", normalized_email, exc)
            email_sent = False

        return {
            "user_id": user_id,
            "email": normalized_email,
            "full_name": full_name,
            "role": role,
            "is_verified": False,
            "email_sent": email_sent,
        }

    def authenticate_user(self, email: str, password: str) -> dict[str, Any]:
        """Authenticate credentials, enforce is_verified check, and issue JWT."""
        normalized_email = email.lower().strip()
        user = users_collection.find_one({"email": normalized_email})

        if not user or not verify_password(password, user["hashed_password"]):
            raise InvalidCredentialsError("Incorrect email or password")

        if not user.get("is_active", True):
            raise AccountDisabledError("Your account is disabled")

        # Explicit check for is_verified (defaults to False if False)
        # Note: If is_verified is explicitly False, block login
        if user.get("is_verified") is False:
            raise EmailVerificationRequiredError("Email verification required.")

        access_token = create_access_token(user_id=str(user["_id"]))

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(user["_id"]),
                "email": user["email"],
                "full_name": user.get("full_name"),
                "role": user["role"],
                "is_verified": user.get("is_verified", True),
            },
        }

    def verify_email(self, email: str, code: str) -> dict[str, Any]:
        """Verify code against Redis, update user in MongoDB, and issue JWT."""
        normalized_email = email.lower().strip()

        # Check user existence
        user = users_collection.find_one({"email": normalized_email})
        if not user:
            raise InvalidCredentialsError("User account not found")

        if user.get("is_verified") is True:
            return {
                "message": "Email is already verified",
                "is_verified": True,
                "already_verified": True,
            }

        # Verify through verification service
        verification_service.verify_code(normalized_email, code)

        # Update MongoDB
        now = datetime.now(timezone.utc)
        users_collection.update_one(
            {"_id": user["_id"]},
            {
                "$set": {
                    "is_verified": True,
                    "email_verified_at": now,
                    "updated_at": now,
                }
            },
        )

        # Generate JWT access token for instant login
        access_token = create_access_token(user_id=str(user["_id"]))

        return {
            "message": "Email verified successfully",
            "is_verified": True,
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(user["_id"]),
                "email": user["email"],
                "full_name": user.get("full_name"),
                "role": user["role"],
                "is_verified": True,
            },
        }

    async def resend_verification_code(self, email: str) -> dict[str, Any]:
        """Resend verification code if user exists and is not yet verified."""
        normalized_email = email.lower().strip()
        user = users_collection.find_one({"email": normalized_email})

        # To avoid email enumeration while providing safe feedback:
        if not user:
            return {
                "message": "If an account exists with this email, a verification code has been sent."
            }

        if user.get("is_verified") is True:
            return {
                "message": "Account is already verified. You can log in directly."
            }

        # Enforces cooldown & generates new code
        code = verification_service.create_verification_code(normalized_email)

        # Send email
        await email_service.send_verification_email(
            to_email=normalized_email,
            full_name=user.get("full_name", "User"),
            code=code,
        )

        return {
            "message": "A new verification code has been sent to your email."
        }


auth_service = AuthService()
