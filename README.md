# FastAPI Modern — Async REST API

High-performance async REST API built with **FastAPI 0.136**, **SQLAlchemy 2.0** (async), **Dramatiq** (task queue), **aiokafka** (event streaming), and **Redis** (cache + pub/sub). OAuth2 authentication with pluggable providers (Keycloak, Auth0, Okta, Authentik, Zitadel).

---

## Quick Start

### 1. Install dependencies
```bash
uv sync
```

### 2. Configure environment
```bash
cp .env.example .env
# Edit .env with your database, Redis, Kafka, and OAuth2 settings
```

### 3. Run migrations
```bash
uv run alembic upgrade head
```

### 4. Start the API
```bash
uv run uvicorn app.main:app --reload --port 8080
```

### 5. Verify
```bash
curl http://localhost:8080/docs  # Swagger UI
curl http://localhost:8080/api/v1/openapi.json  # OpenAPI schema
```

---

## Architecture Decisions

### Why DDD-lite?
Separates business logic from infrastructure concerns. `domain/` has **zero framework imports** — pure Python dataclasses and exceptions. This makes business logic testable without FastAPI, SQLAlchemy, or any other framework.

### Why Dramatiq over Celery or Taskiq?
- **Battle-tested**: Years in production across many projects
- **Async-native**: `AsyncIO` middleware lets you write `async def` tasks
- **Result backend**: `Message.get_result(block=True, timeout=...)` — wait synchronously from an API endpoint
- **Exponential backoff**: Built-in via `Retry` middleware
- **Redis**: Single broker for both Dramatiq and cache (simpler ops)

### Why aiokafka over Faust or Bytewax?
- **Lightweight**: No RocksDB, no WAL overhead
- **Sufficient**: Your use case is Kafka → Redis pub/sub → WebSocket broadcast
- **Battle-tested**: Core library used by many production systems
- **Tradeoff**: If you later need stateful stream processing (joins, time windows), add Faust then

### Why aiokafka over confluent-kafka?
- **Native asyncio**: aiokafka is async-first; confluent-kafka is a C-binding wrapper
- **Pythonic**: Cleaner API, no C compilation required

### Why Redis for both cache and Dramatiq?
Shared broker simplifies infrastructure — one Redis instance serves multiple purposes. Use `redis://redis:6379` in docker-compose for all services.

### Why OAuth2 over built-in JWT?
- No need to manage token signing keys
- Centralized auth (Keycloak, Auth0, etc.) handles sessions, MFA, SSO
- JWT validation happens via JWKS endpoint — no round-trip to auth server on every request

---

## Project Structure

```
app/
├── domain/                     # Pure business logic — NO framework imports
│   ├── auth/entities.py       # OAuth2UserInfo, TokenExpired, InvalidToken
│   ├── users/entities.py      # User dataclass
│   └── events/entities.py     # Domain event dataclasses
├── application/                # Use cases + port interfaces (ABC)
│   ├── auth/ports.py         # TokenValidator, UserInfoFetcher
│   ├── auth/factory.py       # get_oauth2_provider()
│   └── users/
│       ├── ports.py          # UserRepository
│       └── use_cases.py      # list_users, get_user, create_user, etc.
├── infrastructure/             # Implements application ports
│   ├── persistence/
│   │   ├── base.py           # SQLAlchemy declarative_base
│   │   ├── database.py       # async engine, AsyncSessionLocal
│   │   ├── models/           # SQLAlchemy ORM models
│   │   └── repositories/     # SQLAlchemyUserRepository
│   ├── auth/oauth2_providers/  # Keycloak, Auth0, Okta, Authentik, Zitadel
│   ├── events/               # KafkaEventProducer, KafkaEventConsumer
│   └── cache/redis_client.py # Redis cache + pub/sub
├── api/                       # REST/WebSocket endpoints
│   ├── endpoints/auth/        # login.py, dependencies.py
│   ├── endpoints/users/       # CRUD
│   ├── endpoints/websocket.py # /ws/{channel}
│   └── schemas/               # Pydantic V2 schemas
├── middleware/
│   ├── auth.py               # OAuth2Middleware
│   ├── db_exceptions.py       # DB exception → JSON response
│   └── validation.py         # Pydantic validation → JSON response
├── tasks/                     # Dramatiq task queue
│   └── example.py            # Example tasks
└── main.py                   # FastAPI app, lifespan, routers
```

---

## Development Workflows

### Create a New CRUD Endpoint

**Step 1: Create the domain entity**

```python
# app/domain/entities/product.py
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Product:
    id: str
    name: str
    price: float
    stock: int
    created_at: datetime
    updated_at: datetime
```

**Step 2: Create the SQLAlchemy model**

```python
# app/infrastructure/persistence/models/product_model.py
import uuid
from sqlalchemy import Column, String, Numeric, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy_utils import Timestamp
from app.infrastructure.persistence.base import Base

class ProductModel(Base, Timestamp):
    __tablename__ = "products"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    stock = Column(Integer, default=0)
```

**Step 3: Generate and apply the migration**

```bash
uv run alembic revision --autogenerate -m "add products table"
uv run alembic upgrade head
```

**Step 4: Create the repository port and implementation**

```python
# app/application/products/ports.py
from abc import ABC, abstractmethod
from typing import List
from app.domain.entities.product import Product

class ProductRepository(ABC):
    @abstractmethod
    async def get_by_id(self, product_id: str) -> Product | None: ...
    @abstractmethod
    async def get_multi(self, skip: int, limit: int) -> List[Product]: ...
    @abstractmethod
    async def create(self, product: Product) -> Product: ...
```

```python
# app/infrastructure/persistence/repositories/product_repository.py
from typing import List
from sqlalchemy import select
from app.domain.entities.product import Product
from app.application.products.ports import ProductRepository
from app.infrastructure.persistence.models.product_model import ProductModel
from app.infrastructure.persistence.database import AsyncSessionLocal

class SQLAlchemyProductRepository(ProductRepository):
    async def get_by_id(self, product_id: str) -> Product | None:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(ProductModel).where(ProductModel.id == product_id)
            )
            model = result.scalar_one_or_none()
            return self._to_domain(model) if model else None

    # ... implement other methods
```

**Step 5: Create Pydantic schemas**

```python
# app/api/schemas/product.py
from pydantic import BaseModel, ConfigDict
from uuid import UUID

class ProductSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    price: float
    stock: int

class ProductCreate(BaseModel):
    name: str
    price: float
    stock: int = 0
```

**Step 6: Create the endpoint**

```python
# app/api/endpoints/products/product.py
from fastapi import APIRouter, Depends, HTTPException
from app.application.products.ports import ProductRepository
from app.application.products.use_cases import list_products, get_product
from app.api.schemas.product import ProductSchema, ProductCreate
from app.infrastructure.persistence.repositories.product_repository import SQLAlchemyProductRepository

router = APIRouter()

@router.get("/products", response_model=list[ProductSchema])
async def list_products_endpoint(skip: int = 0, limit: int = 100):
    repo = SQLAlchemyProductRepository()
    return await list_products(repo, skip, limit)

@router.get("/products/{product_id}", response_model=ProductSchema)
async def get_product_endpoint(product_id: str):
    repo = SQLAlchemyProductRepository()
    try:
        return await get_product(repo, product_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Product not found")
```

**Step 7: Register the router in main.py**

```python
# app/main.py
from app.api.endpoints.products.product import router as products_router
app.include_router(products_router, prefix=settings.api_v1_str)
```

**Step 8: Create tests**

```python
# app/tests/test_products.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_list_products():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/products")
        assert response.status_code == 200
```

---

### Create a New Dramatiq Task

**1. Define the task:**

```python
# app/tasks/notifications.py
import dramatiq
from dramatiq.middleware import AsyncIO

@dramatiq.actor(
    async_=True,              # Uses AsyncIO middleware
    min_backoff=1000,         # 1s initial backoff
    max_backoff=30000,        # 30s max backoff
    max_retries=5,
    retry_when=lambda e: isinstance(e, TransientError),
)
async def send_email(to: str, subject: str, body: str) -> dict:
    # Your email sending logic here
    await email_client.send(to=to, subject=subject, body=body)
    return {"sent_to": to, "subject": subject}
```

**2. Send a task from an API endpoint (fire-and-forget):**

```python
@router.post("/orders/{order_id}/notify")
async def notify_order(order_id: str):
    order = await get_order(order_id)
    send_email.send(order.email, "Order confirmed", f"Order {order_id} is confirmed")
    return {"message": "Notification queued"}
```

**3. Send a task and wait for result (blocking):**

```python
@router.post("/orders/{order_id}/invoice")
async def generate_invoice(order_id: str):
    order = await get_order(order_id)
    message = generate_invoice.send(order_id)  # Returns immediately
    result = message.get_result(block=True, timeout=30000)  # Wait up to 30s
    return {"invoice_url": result["url"]}
```

**4. Run the worker:**

```bash
uv run dramatiq -m app.tasks
```

For auto-reload during development:
```bash
uv run dramatiq -m app.tasks --watch
```

---

### Create a Kafka Event Producer

```python
# Emit an event from anywhere (e.g., after creating a user)
from app.infrastructure.events.kafka_producer import KafkaEventProducer

await KafkaEventProducer.emit("user_events", {
    "event": "user.created",
    "user_id": str(new_user.id),
    "email": new_user.email,
})
```

**Note:** Kafka events are fire-and-forget. For guaranteed delivery with retries, use Dramatiq tasks instead.

---

### Run the Kafka Consumer

```bash
# Start the Kafka consumer (connects to broker, processes events)
uv run python -m app.infrastructure.events.kafka_consumer
```

The consumer runs in a loop with exponential backoff retry on transient errors.

---

### Run the WebSocket Server

WebSockets are integrated into the main FastAPI app:

```bash
uv run uvicorn app.main:app --reload --port 8080
```

Connect with a valid OAuth2 Bearer token:
```javascript
const ws = new WebSocket(
  `ws://localhost:8080/api/v1/ws/channel_name?token=${accessToken}`
);
```

---

## Debugging

### Watch logs in real-time
```bash
uv run uvicorn app.main:app --reload --port 8080 --log-level debug
```

### Interactive debugger
```bash
uv run debugpy -m uvicorn app.main:app --reload
# Then attach VSCode/PyCharm to port 5678
```

### Check OpenAPI schema
```bash
curl http://localhost:8080/api/v1/openapi.json | jq '.paths | keys'
```

### Verify middleware order
```python
# Middleware executes in reverse order of addition
app.add_middleware(AuthMiddleware)      # 3rd (innermost)
app.add_middleware(DBExceptionMiddleware)  # 2nd
app.add_middleware(FieldValidationMiddleware)  # 1st (outermost)
```

### Inspect Dramatiq queues
```bash
# With Redis, use redis-cli
redis-cli LLEN dramatiq.default
redis-cli LRANGE dramatiq.default 0 -1
```

---

## Testing

### Run all tests
```bash
uv run pytest app/tests/ -v
```

### Run with coverage
```bash
uv run pytest --cov=app --cov-report=html app/tests/
open htmlcov/index.html
```

### Run specific test file
```bash
uv run pytest app/tests/test_user.py -v
```

### Run tests matching a pattern
```bash
uv run pytest -v -k "test_list"
```

### Write a test with mock OAuth2 provider
```python
# app/tests/conftest.py already provides MockOAuth2Provider
# Use it by overriding the dependency:

@pytest.mark.asyncio
async def test_protected_endpoint(client, mock_oauth2_provider):
    app.dependency_overrides[get_oauth2_provider] = lambda: mock_oauth2_provider
    response = await client.get("/api/v1/users", headers={"Authorization": "Bearer valid_token"})
    assert response.status_code == 200
    app.dependency_overrides.clear()
```

### Test with a real database
Set environment variables for your test database:
```bash
DATABASE_PORT=5432 DATABASE_SERVER=localhost DATABASE_USER=test \
DATABASE_PASSWORD=test DATABASE_DB=test_db \
uv run pytest app/tests/ -v
```

---

## Docker / Container Environment

### Build and run
```bash
docker-compose build
docker-compose up
```

### Run only the API
```bash
docker build -t fast-api-app .
docker run -p 8080:8080 --env-file .env fast-api-app
```

### Run the API + worker together
```bash
docker-compose up
# docker-compose.yml starts:
#   - postgres, redis, rabbitmq, kafka (infrastructure)
#   - app (API server)
#   - worker (Dramatiq consumer)
```

### Environment variables in Docker
All settings come from `.env`. Make sure:
- `DATABASE_SERVER=postgres` (the docker-compose service name)
- `REDIS_URL=redis://redis:6379`
- `RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672`
- `KAFKA_BOOTSTRAP_SERVERS=kafka:9092`

### Health check
```bash
curl http://localhost:8080/health 2>/dev/null || echo "No /health endpoint"
```

---

## Code Quality

### Lint
```bash
uv run ruff check app/           # Find issues
uv run ruff check app/ --fix    # Auto-fix
```

### Format
```bash
uv run ruff format app/
```

### Type check
```bash
uv run mypy app/
```

### Dead code detection
```bash
uv run vulture app/ --min-confidence 80
# Or ignore unused code:
uv run vulture app/ --min-confidence 80 --ignore-names="db_*" "unused_*"
```

### Full quality check (CI-like)
```bash
uv run ruff check app/ && uv run mypy app/ && uv run vulture app/ --min-confidence 80
```

---

## Environment Variables

```env
# Database
DATABASE_PORT=5432
DATABASE_SERVER=localhost
DATABASE_USER=app_user
DATABASE_PASSWORD=changeme
DATABASE_DB=app_db

# OAuth2 (configure your provider)
OAUTH2_PROVIDER=keycloak           # keycloak | auth0 | okta | authentik | zitadel
OAUTH2_SERVER_URL=http://localhost:8080/realms/myrealm/
OAUTH2_REALM=myrealm
OAUTH2_CLIENT_ID=myclient
OAUTH2_CLIENT_SECRET=mysecret

# App
SECRET_KEY=change-me-with-openssl-rand-hex-32
BACKEND_CORS_ORIGINS=http://localhost

# Infrastructure (optional — defaults provided)
REDIS_URL=redis://redis:6379
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
```

---

## Troubleshooting

### "Module not found" errors
```bash
uv sync  # Reinstall dependencies
```

### Database connection errors
- Check `DATABASE_SERVER` matches your Postgres host
- In Docker: `DATABASE_SERVER=postgres`
- Verify PostgreSQL is running: `nc -zv localhost 5432`

### OAuth2 validation fails
- Ensure `OAUTH2_SERVER_URL` ends with `/` before the realm
- Check `OAUTH2_CLIENT_ID` matches the provider config
- Verify JWKS endpoint is reachable from the app

### Dramatiq worker not processing tasks
- Check Redis is running: `redis-cli ping`
- Verify worker is connected: look for "Connected to Redis" in worker logs
- Check the queue: `redis-cli LLEN dramatiq.default`

### Kafka consumer not receiving events
- Verify Kafka is running: `nc -zv kafka 9092`
- Check topic exists: list topics in Kafka broker UI
- Consumer group lag: check Kafka consumer group status
