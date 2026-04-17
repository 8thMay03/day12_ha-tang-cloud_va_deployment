import time
import logging
from collections import defaultdict, deque
from fastapi import HTTPException
from app.config import settings

logger = logging.getLogger(__name__)

# Fallback in-memory
_rate_windows: dict[str, deque] = defaultdict(deque)

try:
    import redis
    if settings.redis_url:
        redis_client = redis.Redis.from_url(settings.redis_url, decode_responses=True)
    else:
        redis_client = None
except ImportError:
    redis_client = None

def check_rate_limit(key: str):
    """Ensure the user does not exceed the rate limit per minute using Redis (Stateless)."""
    now = time.time()
    limit = settings.rate_limit_per_minute

    if redis_client:
        try:
            redis_key = f"rate_limit:{key}"
            pipe = redis_client.pipeline()
            # Xóa các request cũ hơn 60s
            pipe.zremrangebyscore(redis_key, 0, now - 60)
            # Thêm request mới
            pipe.zadd(redis_key, {str(now): now})
            # Lấy số lượng
            pipe.zcard(redis_key)
            # Cập nhật TTL
            pipe.expire(redis_key, 60)
            results = pipe.execute()
            
            count = results[2]
            if count > limit:
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded: {limit} req/min",
                    headers={"Retry-After": "60"},
                )
            return
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            logger.warning(f"Redis rate limiter failed, falling back to memory: {e}")
            
    # Fallback in-memory if Redis is absent or failed
    window = _rate_windows[key]
    while window and window[0] < now - 60:
        window.popleft()
        
    if len(window) >= limit:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded: {limit} req/min",
            headers={"Retry-After": "60"},
        )
    window.append(now)
