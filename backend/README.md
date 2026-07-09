# Backend (FastAPI)

## Run locally

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API starts even when Redis is down; aggregate health reports `degraded` when Redis ping fails.

## Redis setup

Redis is used for sessions, cache, rate limits, queues, and operational state. Configuration is **environment-only** (never hardcoded in code).

### Connection options

1. **URL (preferred when provided)** — set `REDIS_URL` (supports `redis://` and `rediss://`):

   ```env
   REDIS_URL=redis://localhost:6379/0
   ```

2. **Component variables (fallback)** — used when `REDIS_URL` is unset:

   | Variable | Default | Description |
   |----------|---------|-------------|
   | `REDIS_HOST` | `localhost` | Redis hostname |
   | `REDIS_PORT` | `6379` | Redis port |
   | `REDIS_PASSWORD` | *(empty)* | Password (optional) |
   | `REDIS_DB` | `0` | Database index |
   | `REDIS_SSL` | `false` | Use `rediss://` when composing URL |

### Pool and resilience

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_ENABLED` | `true` | Enable Redis integration |
| `REDIS_KEY_PREFIX` | `xreminder` | Key namespace prefix |
| `REDIS_MAX_CONNECTIONS` | `10` | Async pool size |
| `REDIS_SOCKET_TIMEOUT` | `5.0` | Command/socket timeout (seconds) |
| `REDIS_SOCKET_CONNECT_TIMEOUT` | `5.0` | Connect timeout (seconds) |
| `REDIS_HEALTH_CHECK_INTERVAL` | `30` | Pool health check interval |
| `REDIS_RETRY_MAX_ATTEMPTS` | `3` | Reconnect/retry attempts |
| `REDIS_RETRY_BASE_DELAY` | `0.5` | Retry backoff base (seconds) |
| `REDIS_RETRY_MAX_DELAY` | `10.0` | Retry backoff cap (seconds) |

### TTL defaults (seconds)

| Variable | Default | Purpose |
|----------|---------|---------|
| `REDIS_TTL_SESSION` | `86400` | Session keys (sliding refresh on read) |
| `REDIS_TTL_CACHE` | `300` | Application cache entries |
| `REDIS_TTL_TEMP` | `300` | Short-lived temp tokens |
| `REDIS_TTL_SCHEDULER_LOCK` | `60` | Scheduler lock keys |

### Architecture

- `app/infrastructure/redis/connection.py` — singleton `RedisManager`, async pool, auto-reconnect, graceful shutdown in app lifespan
- `app/repositories/redis_repository.py` — low-level Redis commands + JSON serialization
- `app/services/cache_service.py` — namespaced cache (get/set/delete/increment/expire/pattern delete)
- `app/infrastructure/redis/session_store.py` — create/refresh/delete sessions with expiration
- `app/infrastructure/redis/testing_helpers.py` — internal ping/flush (dev-only)/config validation

On startup, `lifespan` calls `redis_manager.connect()`; shutdown calls `disconnect()`.

## Health endpoints

| Path | Description |
|------|-------------|
| `GET /api/v1/health` | Service health (includes Redis ping in checks) |
| `GET /api/v1/health/redis` | Dedicated Redis health |
| `GET /health/redis` | Root Redis probe (same payload shape) |
| `GET /healthz` | Legacy aggregate probe |

### `GET /health/redis` response shape

Wrapped in standard `APIResponse`; `data` fields:

```json
{
  "connected": true,
  "latency_ms": 1.23,
  "pool": {
    "status": "connected",
    "max_connections": 10,
    "in_use": 0,
    "available": 1,
    "exhausted": false
  },
  "server_version": "7.2.4",
  "detail": null
}
```

## OpenAPI

- `GET /docs` — Swagger UI
