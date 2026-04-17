import time
import logging
from datetime import datetime
from fastapi import HTTPException
from app.config import settings

logger = logging.getLogger(__name__)

# Fallback in-memory
_monthly_cost = 0.0
_cost_reset_month = time.strftime("%Y-%m")

try:
    import redis
    if settings.redis_url:
        redis_client = redis.Redis.from_url(settings.redis_url, decode_responses=True)
    else:
        redis_client = None
except ImportError:
    redis_client = None

def check_and_record_cost(user_id: str, input_tokens: int, output_tokens: int):
    """Enforce monthly budget based on token usage using Redis (Stateless)."""
    global _monthly_cost, _cost_reset_month
    
    cost = (input_tokens / 1000) * 0.00015 + (output_tokens / 1000) * 0.0006
    month_key = datetime.now().strftime("%Y-%m")
    
    if redis_client:
        try:
            key = f"budget:{user_id}:{month_key}"
            current = float(redis_client.get(key) or 0)
            
            if current + cost > settings.monthly_budget_usd:
                raise HTTPException(status_code=402, detail="Monthly budget exhausted. Please upgrade plan.")
            
            redis_client.incrbyfloat(key, cost)
            redis_client.expire(key, 32 * 24 * 3600)  # 32 days
            return
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            logger.warning(f"Redis cost guard failed, falling back to memory: {e}")
            
    # Fallback in-memory
    if month_key != _cost_reset_month:
        _monthly_cost = 0.0
        _cost_reset_month = month_key
        
    if _monthly_cost + cost > settings.monthly_budget_usd:
        raise HTTPException(status_code=402, detail="Monthly budget exhausted. Please upgrade plan.")
        
    _monthly_cost += cost

def get_current_cost(user_id: str) -> float:
    """Return the current monthly cost."""
    month_key = datetime.now().strftime("%Y-%m")
    if redis_client:
        try:
            return float(redis_client.get(f"budget:{user_id}:{month_key}") or 0)
        except Exception:
            pass
    return _monthly_cost
