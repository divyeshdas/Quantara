import hashlib
import json
import redis.asyncio as aioredis
from typing import Any, Optional
from .config import get_settings


_redis: Optional[aioredis.Redis] = None


async def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        settings = get_settings()
        _redis = aioredis.from_url(settings.redis_url, decode_responses=True)
    return _redis


async def close_redis():
    global _redis
    if _redis:
        await _redis.aclose()
        _redis = None


def make_cache_key(model: str, current_rate: float, horizon_months: int, n_paths: int) -> str:
    rate_str = f"{round(current_rate, 2):.2f}"
    raw = f"{model}:{rate_str}:{horizon_months}:{n_paths}"
    return "sim:" + hashlib.md5(raw.encode()).hexdigest()


async def get_cached(key: str) -> Optional[dict]:
    r = await get_redis()
    val = await r.get(key)
    if val:
        return json.loads(val)
    return None


async def set_cached(key: str, data: dict, ttl: int | None = None) -> None:
    r = await get_redis()
    settings = get_settings()
    ttl = ttl or settings.cache_ttl_seconds
    await r.setex(key, ttl, json.dumps(data))
