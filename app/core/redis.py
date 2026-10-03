import json
from typing import Any, Optional
import redis.asyncio as redis
from app.core.config import settings
from app.core.logging import logger


class RedisService:
    def __init__(self):
        self._redis_client: Optional[redis.Redis] = None
        self._in_memory_fallback: dict = {}

    async def connect(self) -> None:
        try:
            self._redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
            await self._redis_client.ping()
            logger.info("Connected to Redis successfully.")
        except Exception as e:
            logger.warning("Redis connection failed. Falling back to in-memory store.", error=str(e))
            self._redis_client = None

    async def disconnect(self) -> None:
        if self._redis_client:
            await self._redis_client.close()

    async def get(self, key: str) -> Optional[str]:
        if self._redis_client:
            try:
                return await self._redis_client.get(key)
            except Exception as e:
                logger.warning("Redis get error, using fallback", key=key, error=str(e))
        return self._in_memory_fallback.get(key)

    async def set(self, key: str, value: str, expire_seconds: Optional[int] = None) -> bool:
        if self._redis_client:
            try:
                if expire_seconds:
                    await self._redis_client.setex(key, expire_seconds, value)
                else:
                    await self._redis_client.set(key, value)
                return True
            except Exception as e:
                logger.warning("Redis set error, using fallback", key=key, error=str(e))

        self._in_memory_fallback[key] = value
        return True

    async def delete(self, key: str) -> bool:
        if self._redis_client:
            try:
                await self._redis_client.delete(key)
                return True
            except Exception as e:
                logger.warning("Redis delete error", key=key, error=str(e))
        self._in_memory_fallback.pop(key, None)
        return True

    async def set_json(self, key: str, data: Any, expire_seconds: Optional[int] = None) -> bool:
        return await self.set(key, json.dumps(data), expire_seconds=expire_seconds)

    async def get_json(self, key: str) -> Optional[Any]:
        val = await self.get(key)
        if val:
            try:
                return json.loads(val)
            except json.JSONDecodeError:
                return None
        return None


redis_service = RedisService()
