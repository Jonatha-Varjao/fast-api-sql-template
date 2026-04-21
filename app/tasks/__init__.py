import dramatiq
from dramatiq.brokers.rabbitmq import RabbitmqBroker
from dramatiq.middleware import AsyncIO, Retries
from dramatiq.results import Results
from dramatiq.results.backends import RedisBackend
from app.config import settings

# Broker with middleware stack
broker = RabbitmqBroker(url=settings.rabbitmq_url)
broker.add_middleware(AsyncIO())
broker.add_middleware(Results(backend=RedisBackend(url=settings.redis_url)))
broker.add_middleware(Retries(min_backoff=1000, max_backoff=30000, max_retries=5))

dramatiq.set_broker(broker)