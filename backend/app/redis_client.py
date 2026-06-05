"""
Redis client with in-memory fallback when Redis is unavailable.
"""
import json
from typing import Optional

_inmemory_cache: dict = {}
_redis_available = False
_redis_client = None


async def _init_redis():
    global _redis_available, _redis_client
    if _redis_client is not None:
        return _redis_client if _redis_available else None
    try:
        import redis.asyncio as redis
        from app.config import settings
        client = redis.from_url(settings.redis_url, decode_responses=True)
        await client.ping()
        _redis_client = client
        _redis_available = True
        print("Redis connected successfully")
        return _redis_client
    except Exception:
        _redis_available = False
        _redis_client = "unavailable"
        print("Redis unavailable, using in-memory cache fallback")
        return None


class CacheClient:
    """Unified cache interface with Redis or in-memory fallback."""

    async def get(self, key: str) -> Optional[str]:
        client = await _init_redis()
        if client and client != "unavailable":
            try:
                return await client.get(key)
            except Exception:
                pass
        return _inmemory_cache.get(key)

    async def set(self, key: str, value: str, ex: int = 3600):
        client = await _init_redis()
        if client and client != "unavailable":
            try:
                await client.set(key, value, ex=ex)
                return
            except Exception:
                pass
        _inmemory_cache[key] = value


redis_client = CacheClient()


async def get_redis():
    return redis_client
