from typing import Optional
from fastapi import Request, HTTPException, status
from app.core.redis import redis_service
from app.core.config import settings
from app.core.logging import logger


async def check_rate_limit(client_ip: str, key_prefix: str = "rate_limit", max_requests: int = settings.RATE_LIMIT_PER_MINUTE) -> bool:
    """Basic rate limiting using Redis/fallback store."""
    cache_key = f"{key_prefix}:{client_ip}"
    current = await redis_service.get(cache_key)

    if current is not None:
        count = int(current)
        if count >= max_requests:
            logger.warning("Rate limit exceeded", ip=client_ip, count=count)
            return False
        await redis_service.set(cache_key, str(count + 1), expire_seconds=60)
    else:
        await redis_service.set(cache_key, "1", expire_seconds=60)

    return True


async def rate_limit_middleware(request: Request) -> None:
    client_ip = request.client.host if request.client else "127.0.0.1"
    is_allowed = await check_rate_limit(client_ip)
    if not is_allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please slow down your requests."
        )
