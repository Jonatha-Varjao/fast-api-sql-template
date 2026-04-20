import dramatiq

@dramatiq.actor(
    async_=True,           # async actor via AsyncIO middleware
    min_backoff=1000,      # 1s initial backoff
    max_backoff=30000,     # 30s max backoff
    max_retries=5,
    retry_when=lambda e: isinstance(e, TransientError),  # only retry transient errors
)
async def send_notification(email: str, message: str) -> dict:
    await send_email(email, message)
    return {"sent_to": email}

# In an API endpoint — send task and wait for result:
@router.post("/notify")
async def notify(email: str, message: str):
    # Send to queue, get message
    message = send_notification.send(email, message)
    # Wait synchronously for result (max 10s)
    result = message.get_result(block=True, timeout=10000)
    return result