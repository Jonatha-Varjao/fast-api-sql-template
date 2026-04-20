import json
from typing import Optional, Any
import redis.asyncio as redis
from app.config import settings

class RedisClient:
    async def connect(self) -> None:
        self._pool = redis.ConnectionPool.from_url(settings.redis_url, decode_responses=True, max_connections=50)
        self._client = redis.Redis(connection_pool=self._pool)

    async def disconnect(self) -> None:
        if self._client:
            await self._client.aclose()
        if self._pool:
            await self._pool.disconnect()

    async def get(self, key: str) -> Optional[Any]:
        value = await self._client.get(key)
        return json.loads(value) if value else None

    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> None:
        serialized = json.dumps(value)
        if expire:
            await self._client.setex(key, expire, serialized)
        else:
            await self._client.set(key, serialized)

    async def delete(self, key: str) -> None:
        await self._client.delete(key)

    async def publish(self, channel: str, message: Any) -> None:
        await self._client.publish(channel, json.dumps(message))

    async def subscribe(self, channel: str):
        pubsub = self._client.pubsub()
        await pubsub.subscribe(channel)
        return pubsub

redis_client = RedisClient()