import pytest
from unittest.mock import MagicMock, patch
from app.services.verification_service import (
    VerificationService,
    CooldownActiveError,
    InvalidCodeError,
    MaxAttemptsExceededError,
    CodeExpiredOrNotFoundError,
)


@pytest.fixture
def mock_redis():
    client = MagicMock()
    with patch("app.services.verification_service.get_redis_client", return_value=client):
        yield client


def test_generate_code_format():
    service = VerificationService()
    for _ in range(50):
        code = service.generate_code()
        assert len(code) == 6
        assert code.isdigit()


def test_create_verification_code_stores_in_redis(mock_redis):
    service = VerificationService()
    mock_redis.ttl.return_value = -2  # no cooldown
    pipe = MagicMock()
    mock_redis.pipeline.return_value = pipe

    code = service.create_verification_code("user@example.com")
    assert len(code) == 6
    assert pipe.set.call_count == 3
    assert pipe.execute.called


def test_create_verification_code_enforces_cooldown(mock_redis):
    service = VerificationService()
    mock_redis.ttl.return_value = 45  # 45s remaining

    with pytest.raises(CooldownActiveError, match="Please wait 45 seconds"):
        service.create_verification_code("user@example.com")


def test_verify_code_success(mock_redis):
    service = VerificationService()
    mock_redis.eval.return_value = 1  # 1 = Success

    result = service.verify_code("user@example.com", "123456")
    assert result is True
    assert mock_redis.delete.called


def test_verify_code_expired_or_not_found(mock_redis):
    service = VerificationService()
    mock_redis.eval.return_value = -1

    with pytest.raises(CodeExpiredOrNotFoundError):
        service.verify_code("user@example.com", "123456")


def test_verify_code_max_attempts_exceeded(mock_redis):
    service = VerificationService()
    mock_redis.eval.return_value = -2

    with pytest.raises(MaxAttemptsExceededError):
        service.verify_code("user@example.com", "123456")


def test_verify_code_mismatch_shows_remaining(mock_redis):
    service = VerificationService()
    mock_redis.eval.return_value = -3
    mock_redis.get.return_value = "2"  # 2 attempts made

    with pytest.raises(InvalidCodeError) as exc_info:
        service.verify_code("user@example.com", "999999")
    assert exc_info.value.remaining_attempts == 3
