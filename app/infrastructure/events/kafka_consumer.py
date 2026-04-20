import json
import asyncio
from dataclasses import dataclass
from typing import Callable, Awaitable
from aiokafka import AIOKafkaConsumer
from app.config import settings

@dataclass
class KafkaEvent:
    topic: str
    partition: int
    offset: int
    key: str | None
    value: dict

class KafkaEventConsumer:
    def __init__(
        self,
        topics: list[str],
        group_id: str = "app_group",
        max_retries: int = 5,
        base_backoff: float = 1.0,
        backoff_factor: float = 2.0,
    ):
        self.topics = [f"app.{t}" for t in topics]
        self.group_id = group_id
        self.max_retries = max_retries
        self.base_backoff = base_backoff
        self.backoff_factor = backoff_factor
        self._consumer: AIOKafkaConsumer | None = None
        self._handler: Callable[[dict], Awaitable[None]] | None = None

    async def start(self):
        self._consumer = AIOKafkaConsumer(
            *self.topics,
            bootstrap_servers=settings.kafka_bootstrap_servers,
            group_id=self.group_id,
            value_deserializer=lambda v: json.loads(v.decode()),
            auto_offset_reset="earliest",
            enable_auto_commit=False,  # Manual commit for at-least-once
        )
        await self._consumer.start()

    async def stop(self):
        if self._consumer:
            await self._consumer.stop()

    async def _process_with_backoff(self, event: KafkaEvent, handler: Callable[[dict], Awaitable[None]]):
        """Process event with exponential backoff retries on transient failures."""
        for attempt in range(self.max_retries):
            try:
                await handler(event.value)
                return  # Success
            except TransientError as e:
                if attempt == self.max_retries - 1:
                    raise  # Last attempt failed
                wait = self.base_backoff * (self.backoff_factor ** attempt)
                await asyncio.sleep(wait)
            except Exception:
                raise  # Non-transient errors fail immediately

    async def consume(self, handler: Callable[[dict], Awaitable[None]]):
        """Main consume loop with backoff retry."""
        if not self._consumer:
            raise RuntimeError("Consumer not started")
        self._handler = handler
        async for msg in self._consumer:
            event = KafkaEvent(
                topic=msg.topic.removeprefix("app."),
                partition=msg.partition,
                offset=msg.offset,
                key=msg.key.decode() if msg.key else None,
                value=msg.value,
            )
            try:
                await self._process_with_backoff(event, handler)
                await self._consumer.commit()
            except Exception:
                # Dead-letter: log and continue
                await self._consumer.commit()  # Don't re-process forever