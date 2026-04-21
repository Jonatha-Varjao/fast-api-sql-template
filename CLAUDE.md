# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FastAPI 0.136 + SQLAlchemy 2.0 (async) + PostgreSQL REST API with OAuth2 authentication. Uses `uv` for dependency management, Alembic for migrations, Dramatiq for task queues, aiokafka for event streaming, and Redis for caching/pubsub.

## Commands

### Setup & Running
```bash
uv sync --extra dev    # Install all dependencies including dev tools
cp .env.example .env    # Configure environment variables
uv run alembic upgrade head  # Apply migrations
uv run uvicorn app.main:app --reload --port 8080  # Run locally
```

### Migrations
```bash
uv run alembic revision --autogenerate -m "describe change"  # Generate migration
uv run alembic upgrade head                               # Apply migrations
uv run alembic downgrade -1                               # Rollback last migration
```

### Testing
Tests use async fixtures with a live test database. Set env vars before running.
```bash
uv run pytest app/tests/ -v
uv run pytest app/tests/ -v -k "test_name"  # Run specific test
```

### Code Quality
```bash
uv run ruff check app/        # Lint
uv run ruff format app/        # Format
uv run mypy app/               # Type check
uv run vulture app/ --min-confidence 80  # Dead code detection
uv run pytest --cov=app app/tests/  # Coverage report
```

## Architecture

### Layer Dependency Rule
```
domain → application → infrastructure → api
```
- `domain/` — Pure Python (no framework imports), business entities
- `application/` — Use cases + port interfaces (ABC)
- `infrastructure/` — Implements ports (DB, auth providers, messaging, cache)
- `api/` — REST endpoints, schemas, WebSockets

### Directory Structure
```
app/
├── domain/                          # Business logic (no framework deps)
│   ├── auth/entities.py            # OAuth2UserInfo, TokenExpired, InvalidToken
│   ├── users/entities.py           # User dataclass
│   └── events/entities.py          # Domain event dataclasses
├── application/                     # Use cases + ports
│   ├── auth/
│   │   ├── ports.py               # TokenValidator, UserInfoFetcher ABCs
│   │   └── factory.py             # get_oauth2_provider()
│   └── users/
│       ├── ports.py               # UserRepository ABC
│       └── use_cases.py          # list_users, get_user, create_user, etc.
├── infrastructure/                  # Framework implementations
│   ├── persistence/
│   │   ├── base.py                # SQLAlchemy declarative_base
│   │   ├── database.py             # async engine, AsyncSessionLocal, get_db
│   │   ├── models/user_model.py    # UserModel, Environment, Permission, Group
│   │   └── repositories/           # SQLAlchemyUserRepository
│   ├── auth/oauth2_providers/     # Keycloak, Auth0, Okta, Authentik, Zitadel
│   ├── events/                    # KafkaEventProducer, KafkaEventConsumer
│   ├── cache/redis_client.py      # Redis client (cache + pub/sub)
│   └── messaging/                 # (future: additional messaging)
├── api/
│   ├── endpoints/auth/            # login.py, dependencies.py
│   ├── endpoints/users/           # CRUD endpoints
│   ├── schemas/user.py            # Pydantic V2 schemas
│   └── endpoints/websocket.py      # WebSocket endpoint
├── middleware/
│   ├── auth.py                    # OAuth2Middleware
│   ├── db_exceptions.py           # DBException middleware
│   └── validation.py              # FieldValidation middleware
├── tasks/                          # Dramatiq task queue
│   ├── __init__.py                # Broker setup (RabbitMQ + AsyncIO + Retry + Results)
│   └── example.py                 # Example async tasks
├── config.py                       # Pydantic Settings (from .env)
├── main.py                         # FastAPI app entry point
└── tests/
    ├── conftest.py                # Async pytest fixtures
    └── mocks/oauth2_provider.py   # MockOAuth2Provider for tests
```

### Request Flow
```
Request → Middlewares (OAuth2 → DBException → FieldValidation) → Routers → Endpoints
```

### Key Files
- `app/config.py` — Pydantic Settings reading from `.env`, `settings` singleton
- `app/main.py` — FastAPI app with lifespan, CORS, middleware, router includes
- `app/infrastructure/persistence/database.py` — AsyncSessionLocal, get_db generator
- `app/domain/auth/entities.py` — OAuth2UserInfo dataclass
- `app/middleware/auth.py` — OAuth2Middleware (validates Bearer token via provider)
- `app/tasks/__init__.py` — Dramatiq broker (RabbitMQ + AsyncIO + Retries + Results)

### Auth Flow (OAuth2)
- Provider validates JWT via JWKS endpoint
- `get_current_user()` / `require_superuser()` dependency injectors extract `OAuth2UserInfo` from `request.state.user_info`
- Configure via `OAUTH2_PROVIDER` env var (keycloak, auth0, okta, authentik, zitadel)

### Alembic Migrations
Migrations live in `app/alembic/versions/`. The env imports all models to register them on `Base.metadata` before generating migrations.

### Database
- Runtime: `DATABASE_URL` with `asyncpg` driver
- Migrations: `ALEMBIC_URL` with `psycopg2` driver

### Task Queue (Dramatiq)
- Broker: RabbitMQ with AsyncIO, Retry (exponential backoff), Results middleware
- Tasks are async functions decorated with `@dramatiq.actor(async_=True, ...)`
- Worker: `uv run dramatiq -m app.tasks`

### Event Streaming (aiokafka)
- Producer: `KafkaEventProducer.emit(topic, value)` — fire-and-forget
- Consumer: `KafkaEventConsumer` with exponential backoff retry on transient errors

### Redis
- Cache + pub/sub for WebSocket broadcast
- Used by Dramatiq results backend (shared with broker connection)
