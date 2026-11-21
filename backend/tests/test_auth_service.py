import pytest
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock
from bson import ObjectId

from app.services.auth_service import (
    AuthService,
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    AccountDisabledError,
    EmailVerificationRequiredError,
)


@pytest.fixture
def auth_svc():
    return AuthService()


@pytest.mark.asyncio
async def test_register_creates_unverified_user(auth_svc):
    inserted_id = ObjectId()
    with patch("app.services.auth_service.users_collection") as mock_users, \
         patch("app.services.auth_service.candidates_collection") as mock_candidates, \
         patch("app.services.auth_service.verification_service") as mock_verify_svc, \
         patch("app.services.auth_service.email_service.send_verification_email", new_callable=pytest.importorskip("unittest.mock").AsyncMock) as mock_send_email:

        mock_users.find_one.return_value = None
        mock_users.insert_one.return_value = MagicMock(inserted_id=inserted_id)
        mock_verify_svc.create_verification_code.return_value = "654321"

        res = await auth_svc.register_user(
            email="newcandidate@test.com",
            password="SecurePassword123!",
            full_name="New Candidate",
            role="candidate",
        )

        assert res["email"] == "newcandidate@test.com"
        assert res["is_verified"] is False
        assert res["email_sent"] is True
        assert mock_send_email.called

        inserted_doc = mock_users.insert_one.call_args[0][0]
        assert inserted_doc["is_verified"] is False
        assert inserted_doc["email_verified_at"] is None
        assert mock_candidates.insert_one.called


def test_login_rejects_unverified_user(auth_svc):
    with patch("app.services.auth_service.users_collection") as mock_users, \
         patch("app.services.auth_service.verify_password", return_value=True):

        mock_users.find_one.return_value = {
            "_id": ObjectId(),
            "email": "unverified@test.com",
            "hashed_password": "hashed",
            "is_active": True,
            "is_verified": False,
        }

        with pytest.raises(EmailVerificationRequiredError, match="Email verification required."):
            auth_svc.authenticate_user("unverified@test.com", "Password123!")


def test_login_allows_verified_and_legacy_user(auth_svc):
    with patch("app.services.auth_service.users_collection") as mock_users, \
         patch("app.services.auth_service.verify_password", return_value=True), \
         patch("app.services.auth_service.create_access_token", return_value="fake-jwt-token"):

        # 1. Verified user
        mock_users.find_one.return_value = {
            "_id": ObjectId(),
            "email": "verified@test.com",
            "hashed_password": "hashed",
            "is_active": True,
            "is_verified": True,
            "role": "candidate",
            "full_name": "Verified User",
        }
        res1 = auth_svc.authenticate_user("verified@test.com", "Password123!")
        assert res1["access_token"] == "fake-jwt-token"

        # 2. Legacy user without is_verified field (defaults to True)
        mock_users.find_one.return_value = {
            "_id": ObjectId(),
            "email": "legacy@test.com",
            "hashed_password": "hashed",
            "is_active": True,
            "role": "recruiter",
            "full_name": "Legacy Recruiter",
        }
        res2 = auth_svc.authenticate_user("legacy@test.com", "Password123!")
        assert res2["access_token"] == "fake-jwt-token"


def test_verify_email_updates_mongodb_and_returns_jwt(auth_svc):
    user_id = ObjectId()
    with patch("app.services.auth_service.users_collection") as mock_users, \
         patch("app.services.auth_service.verification_service") as mock_verify_svc, \
         patch("app.services.auth_service.create_access_token", return_value="new-access-jwt"):

        mock_users.find_one.return_value = {
            "_id": user_id,
            "email": "verify_me@test.com",
            "is_verified": False,
            "role": "candidate",
            "full_name": "Verify Me",
        }
        mock_verify_svc.verify_code.return_value = True

        res = auth_svc.verify_email("verify_me@test.com", "123456")
        assert res["is_verified"] is True
        assert res["access_token"] == "new-access-jwt"
        assert mock_users.update_one.called
