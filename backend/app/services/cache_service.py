"""
Redis caching service for analysis results and API responses.
"""
import json
from typing import Optional, Dict
from app.redis_client import redis_client

ANALYSIS_CACHE_TTL = 3600  # 1 hour
FACTCHECK_CACHE_TTL = 86400  # 24 hours


async def get_cached_result(key: str) -> Optional[Dict]:
    """Retrieve cached analysis result."""
    try:
        cached = await redis_client.get(f"analysis:{key}")
        if cached:
            return json.loads(cached)
    except Exception:
        pass
    return None


async def cache_result(key: str, result: Dict, ttl: int = ANALYSIS_CACHE_TTL):
    """Cache an analysis result."""
    try:
        await redis_client.set(
            f"analysis:{key}",
            json.dumps(result, default=str),
            ex=ttl,
        )
    except Exception:
        pass  # Cache failures shouldn't break the pipeline


async def get_cached_factcheck(query: str) -> Optional[list]:
    """Retrieve cached fact-check results."""
    try:
        cached = await redis_client.get(f"factcheck:{query[:100]}")
        if cached:
            return json.loads(cached)
    except Exception:
        pass
    return None


async def cache_factcheck(query: str, results: list):
    """Cache fact-check API results."""
    try:
        await redis_client.set(
            f"factcheck:{query[:100]}",
            json.dumps(results, default=str),
            ex=FACTCHECK_CACHE_TTL,
        )
    except Exception:
        pass
