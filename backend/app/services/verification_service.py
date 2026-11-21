import hashlib
import hmac
import logging
import secrets
from dataclasses import dataclass
from typing import Any

from app.core.config import settings
from app.core.redis import get_redis_client

logger = logging.getLogger(__name__)


class VerificationError(Exception):
    """Base exception for verification service errors."""
    pass


class CooldownActiveError(VerificationError):
    """Raised when resend is requested before cooldown expires."""
    def __init__(self, ttl_seconds: int):
        super().__init__(f"Please wait {ttl_seconds} seconds before requesting a new code.")
        self.ttl_seconds = ttl_seconds


class MaxAttemptsExceededError(VerificationError):
    """Raised when maximum verification attempts have been reached."""
    pass


class InvalidCodeError(VerificationError):
    """Raised when verification code does not match."""
    def __init__(self, remaining_attempts: int):
        super().__init__(f"Invalid verification code. {remaining_attempts} attempt(s) remaining.")
        self.remaining_attempts = remaining_attempts


class CodeExpiredOrNotFoundError(VerificationError):
    """Raised when code has expired or does not exist."""
    pass


@dataclass
class VerificationData:
    code: str
    expire_minutes: int


class VerificationService:
    """Manages secure generation, hashing, Redis storage, rate limiting, and verification of codes."""

    # Key prefixes
    PREFIX_CODE = "verify:code:"
    PREFIX_ATTEMPTS = "verify:attempts:"
    PREFIX_COOLDOWN = "verify:cooldown:"

    # Atomic Lua script for verification
    # KEYS[1]: code_key
    # KEYS[2]: attempts_key
    # ARGV[1]: expected_hash
    # ARGV[2]: max_attempts
    # Returns:
    #   1: Success (keys deleted)
    #  -1: Code not found or expired
    #  -2: Max attempts exceeded (keys deleted)
    #  -3: Code mismatch (attempts incremented)
    VERIFY_LUA = """
    local code_val = redis.call('GET', KEYS[1])
    if not code_val then
        return -1
    end

    local current_attempts = tonumber(redis.call('GET', KEYS[2]) or '0')
    if current_attempts >= tonumber(ARGV[2]) then
        redis.call('DEL', KEYS[1], KEYS[2])
        return -2
    end

    if code_val == ARGV[1] then
        redis.call('DEL', KEYS[1], KEYS[2])
        return 1
    else
        local new_attempts = redis.call('INCR', KEYS[2])
        if new_attempts >= tonumber(ARGV[2]) then
            redis.call('DEL', KEYS[1], KEYS[2])
            return -2
        else
            return -3
        end
    end
    """

    def __init__(self) -> None:
        self.expire_seconds = settings.VERIFICATION_CODE_EXPIRE_MINUTES * 60
        self.max_attempts = settings.VERIFICATION_MAX_ATTEMPTS
        self.cooldown_seconds = settings.VERIFICATION_RESEND_COOLDOWN_SECONDS

    @staticmethod
    def _hash_code(email: str, code: str) -> str:
        """Hash the verification code with HMAC-SHA256 salted by SECRET_KEY and email."""
        key = settings.SECRET_KEY.encode("utf-8")
        msg = f"{email.lower().strip()}:{code}".encode("utf-8")
        return hmac.new(key, msg, hashlib.sha256).hexdigest()

    def generate_code(self) -> str:
        """Generate a cryptographically secure 6-digit verification code."""
        return f"{secrets.randbelow(1_000_000):06d}"

    def create_verification_code(self, email: str, force_ignore_cooldown: bool = False) -> str:
        """Generate and store a new verification code in Redis with TTL and cooldown."""
        client = get_redis_client()
        normalized_email = email.lower().strip()

        cooldown_key = f"{self.PREFIX_COOLDOWN}{normalized_email}"
        code_key = f"{self.PREFIX_CODE}{normalized_email}"
        attempts_key = f"{self.PREFIX_ATTEMPTS}{normalized_email}"

        # Check resend cooldown
        if not force_ignore_cooldown:
            ttl = client.ttl(cooldown_key)
            if ttl and ttl > 0:
                raise CooldownActiveError(ttl_seconds=ttl)

        # Generate new 6-digit code
        raw_code = self.generate_code()
        hashed = self._hash_code(normalized_email, raw_code)

        # Atomic transaction: set code, reset attempts, set cooldown
        pipe = client.pipeline()
        pipe.set(code_key, hashed, ex=self.expire_seconds)
        pipe.set(attempts_key, 0, ex=self.expire_seconds)
        pipe.set(cooldown_key, 1, ex=self.cooldown_seconds)
        pipe.execute()

        logger.info("Verification code created and cached for %s", normalized_email)
        return raw_code

    def verify_code(self, email: str, submitted_code: str) -> bool:
        """Verify code atomically using Lua script to prevent race conditions."""
        client = get_redis_client()
        normalized_email = email.lower().strip()

        code_key = f"{self.PREFIX_CODE}{normalized_email}"
        attempts_key = f"{self.PREFIX_ATTEMPTS}{normalized_email}"

        expected_hash = self._hash_code(normalized_email, submitted_code.strip())

        result: int = client.eval(
            self.VERIFY_LUA,
            2,
            code_key,
            attempts_key,
            expected_hash,
            str(self.max_attempts),
        )

        if result == 1:
            # Also clean up any lingering cooldown key
            client.delete(f"{self.PREFIX_COOLDOWN}{normalized_email}")
            logger.info("Email verification succeeded for %s", normalized_email)
            return True
        elif result == -1:
            raise CodeExpiredOrNotFoundError("Verification code has expired or is invalid.")
        elif result == -2:
            raise MaxAttemptsExceededError("Maximum verification attempts exceeded. Please request a new code.")
        elif result == -3:
            current_attempts = int(client.get(attempts_key) or 1)
            remaining = max(0, self.max_attempts - current_attempts)
            raise InvalidCodeError(remaining_attempts=remaining)
        else:
            raise VerificationError("Unknown verification response.")

    def delete_verification_data(self, email: str) -> None:
        """Purge all verification keys for an email."""
        client = get_redis_client()
        normalized_email = email.lower().strip()
        client.delete(
            f"{self.PREFIX_CODE}{normalized_email}",
            f"{self.PREFIX_ATTEMPTS}{normalized_email}",
            f"{self.PREFIX_COOLDOWN}{normalized_email}",
        )


verification_service = VerificationService()
