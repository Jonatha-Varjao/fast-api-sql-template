import dramatiq
from dramatiq.middleware import Retries


class TransientError(Exception):
    """Error that should trigger a retry."""


@dramatiq.actor(
    async_=True,  # async actor via AsyncIO middleware
    min_backoff=1000,  # 1s initial backoff
    max_backoff=30000,  # 30s max backoff
    max_retries=5,
    retry_when=lambda e: isinstance(e, TransientError),
)
async def send_notification(email: str, message: str) -> dict:
    # await send_email(email, message)
    return {"sent_to": email, "message": message}
