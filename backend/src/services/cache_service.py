import redis.asyncio as redis
import json
import pickle
from typing import Any, Optional, Union
from src.config.settings import settings
import logging

logger = logging.getLogger(__name__)


class CacheService:
    """Redis-based caching service for improved performance."""

    def __init__(self):
        """Initialize Redis connection."""
        self.redis_client = None
        self.is_available = False
        self._initialize_redis()

    def _initialize_redis(self):
        """Initialize Redis connection with error handling."""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30,
            )
            self.is_available = True
            logger.info("Redis cache service initialized successfully")
        except Exception as e:
            logger.warning(
                f"Redis initialization failed: {e}. Caching will be disabled."
            )
            self.is_available = False

    async def get(self, key: str, default: Any = None) -> Any:
        """
        Get value from cache.

        Args:
            key: Cache key
            default: Default value if key not found

        Returns:
            Cached value or default
        """
        if not self.is_available:
            return default

        try:
            value = await self.redis_client.get(key)
            if value is None:
                return default

            # Try to parse as JSON first, then as pickle
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                try:
                    return pickle.loads(value.encode("utf-8"))
                except:
                    return value
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return default

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        serialize_json: bool = True,
    ) -> bool:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (None for default TTL)
            serialize_json: Whether to serialize as JSON (vs pickle)

        Returns:
            True if successful, False otherwise
        """
        if not self.is_available:
            return False

        try:
            # Serialize value
            if serialize_json:
                try:
                    serialized_value = json.dumps(value)
                except (TypeError, ValueError):
                    # Fallback to pickle for complex objects
                    serialized_value = pickle.dumps(value).decode("utf-8")
            else:
                serialized_value = pickle.dumps(value).decode("utf-8")

            # Set with TTL
            ttl = ttl or settings.REDIS_CACHE_TTL
            await self.redis_client.setex(key, ttl, serialized_value)
            return True

        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """
        Delete key from cache.

        Args:
            key: Cache key to delete

        Returns:
            True if successful, False otherwise
        """
        if not self.is_available:
            return False

        try:
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.

        Args:
            key: Cache key to check

        Returns:
            True if key exists, False otherwise
        """
        if not self.is_available:
            return False

        try:
            result = await self.redis_client.exists(key)
            return bool(result)
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False

    async def increment(
        self, key: str, amount: int = 1, ttl: Optional[int] = None
    ) -> Optional[int]:
        """
        Increment a numeric value in cache.

        Args:
            key: Cache key
            amount: Amount to increment by
            ttl: TTL for the key if it doesn't exist

        Returns:
            New value or None if error
        """
        if not self.is_available:
            return None

        try:
            # Increment the value
            new_value = await self.redis_client.incrby(key, amount)

            # Set TTL if this is a new key
            if new_value == amount and ttl:
                await self.redis_client.expire(key, ttl)

            return new_value
        except Exception as e:
            logger.error(f"Cache increment error for key {key}: {e}")
            return None

    async def get_many(self, keys: list) -> dict:
        """
        Get multiple values from cache.

        Args:
            keys: List of cache keys

        Returns:
            Dictionary mapping keys to values
        """
        if not self.is_available or not keys:
            return {}

        try:
            values = await self.redis_client.mget(keys)
            result = {}

            for i, key in enumerate(keys):
                value = values[i]
                if value is not None:
                    try:
                        result[key] = json.loads(value)
                    except (json.JSONDecodeError, TypeError):
                        try:
                            result[key] = pickle.loads(value.encode("utf-8"))
                        except:
                            result[key] = value

            return result
        except Exception as e:
            logger.error(f"Cache get_many error for keys {keys}: {e}")
            return {}

    async def set_many(self, mapping: dict, ttl: Optional[int] = None) -> bool:
        """
        Set multiple values in cache.

        Args:
            mapping: Dictionary of key-value pairs
            ttl: Time to live in seconds

        Returns:
            True if successful, False otherwise
        """
        if not self.is_available or not mapping:
            return False

        try:
            # Serialize all values
            serialized_mapping = {}
            for key, value in mapping.items():
                try:
                    serialized_mapping[key] = json.dumps(value)
                except (TypeError, ValueError):
                    serialized_mapping[key] = pickle.dumps(value).decode("utf-8")

            # Set all values
            await self.redis_client.mset(serialized_mapping)

            # Set TTL for all keys if specified
            if ttl:
                pipe = self.redis_client.pipeline()
                for key in mapping.keys():
                    pipe.expire(key, ttl)
                await pipe.execute()

            return True
        except Exception as e:
            logger.error(f"Cache set_many error: {e}")
            return False

    async def clear_pattern(self, pattern: str) -> int:
        """
        Clear all keys matching a pattern.

        Args:
            pattern: Redis key pattern (e.g., "user:*")

        Returns:
            Number of keys deleted
        """
        if not self.is_available:
            return 0

        try:
            keys = await self.redis_client.keys(pattern)
            if keys:
                await self.redis_client.delete(*keys)
                return len(keys)
            return 0
        except Exception as e:
            logger.error(f"Cache clear_pattern error for pattern {pattern}: {e}")
            return 0

    async def get_ttl(self, key: str) -> Optional[int]:
        """
        Get TTL for a key.

        Args:
            key: Cache key

        Returns:
            TTL in seconds or None if key doesn't exist
        """
        if not self.is_available:
            return None

        try:
            ttl = await self.redis_client.ttl(key)
            return ttl if ttl > 0 else None
        except Exception as e:
            logger.error(f"Cache get_ttl error for key {key}: {e}")
            return None

    async def health_check(self) -> bool:
        """
        Check if Redis is healthy.

        Returns:
            True if Redis is responsive, False otherwise
        """
        if not self.is_available:
            return False

        try:
            await self.redis_client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return False

    async def close(self):
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()


# Cache key helpers
class CacheKeys:
    """Helper class for generating consistent cache keys."""

    @staticmethod
    def conversation_history(conversation_id: str) -> str:
        """Generate cache key for conversation history."""
        return f"chat:conversation:{conversation_id}:history"

    @staticmethod
    def knowledge_base_search(query: str, agent: str) -> str:
        """Generate cache key for knowledge base search."""
        query_hash = hash(query.lower().strip())
        return f"kb:search:{agent}:{query_hash}"

    @staticmethod
    def intent_classification(message: str) -> str:
        """Generate cache key for intent classification."""
        message_hash = hash(message.lower().strip())
        return f"intent:classify:{message_hash}"

    @staticmethod
    def user_rate_limit(user_id: str, endpoint: str) -> str:
        """Generate cache key for rate limiting."""
        return f"rate_limit:{endpoint}:{user_id}"

    @staticmethod
    def analytics_data(metric: str, period: str) -> str:
        """Generate cache key for analytics."""
        return f"analytics:{metric}:{period}"


# Global cache instance
cache_service = CacheService()
