import json
import asyncio
from aiokafka import AIOKafkaProducer
from app.config import settings

class KafkaEventProducer:
    _producer: AIOKafkaProducer | None = None

    @classmethod
    async def connect(cls):
        cls._producer = AIOKafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode(),
        )
        await cls._producer.start()

    @classmethod
    async def disconnect(cls):
        if cls._producer:
            await cls._producer.stop()

    @classmethod
    async def emit(cls, topic: str, value: dict, key: str | None = None):
        if not cls._producer:
            raise RuntimeError("Producer not connected")
        await cls._producer.send_and_wait(
            topic=f"app.{topic}", value=value,
            key=key.encode() if key else None,
        )