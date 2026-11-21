import redis
from app.core.config import settings

# Global Redis client instance
redis_client: redis.Redis | None = None


def get_redis_client() -> redis.Redis:
    """Return a thread-safe singleton Redis client."""
    global redis_client
    if redis_client is None:
        redis_client = redis.Redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_timeout=5,
        )
    return redis_client


def close_redis_client() -> None:
    """Close the Redis client connection."""
    global redis_client
    if redis_client is not None:
        redis_client.close()
        redis_client = None
