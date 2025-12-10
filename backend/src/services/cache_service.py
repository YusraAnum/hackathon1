import time
import hashlib
from typing import Any, Optional, Dict
from src.utils.logging import get_logger


logger = get_logger(__name__)


class CacheService:
    """
    Simple in-memory cache service for performance optimization.
    In production, this would be replaced with Redis or similar.
    """

    def __init__(self, default_ttl: int = 300):  # 5 minutes default TTL
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
        logger.info("Cache service initialized")

    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate a cache key from prefix and arguments"""
        key_str = f"{prefix}:{str(args)}:{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_str.encode()).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if it exists and hasn't expired"""
        if key in self.cache:
            entry = self.cache[key]
            if time.time() < entry['expires_at']:
                logger.debug(f"Cache hit for key: {key}")
                return entry['value']
            else:
                # Remove expired entry
                del self.cache[key]
                logger.debug(f"Cache expired for key: {key}")

        logger.debug(f"Cache miss for key: {key}")
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with TTL (time-to-live)"""
        if ttl is None:
            ttl = self.default_ttl

        self.cache[key] = {
            'value': value,
            'expires_at': time.time() + ttl
        }
        logger.debug(f"Cache set for key: {key} with TTL: {ttl}s")

    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        if key in self.cache:
            del self.cache[key]
            logger.debug(f"Cache deleted for key: {key}")
            return True
        return False

    def clear(self) -> None:
        """Clear all cache entries"""
        self.cache.clear()
        logger.info("Cache cleared")

    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate cache entries that match a pattern"""
        keys_to_delete = []
        for key in self.cache:
            if pattern in key:
                keys_to_delete.append(key)

        for key in keys_to_delete:
            del self.cache[key]

        logger.info(f"Invalidated {len(keys_to_delete)} cache entries matching pattern: {pattern}")
        return len(keys_to_delete)


# Global instance
cache_service = CacheService()