# Backend Deployment Guide

## Runtime
- Python 3.11+
- Redis required for full functionality (`REDIS_ENABLED=true`)
- Qdrant optional (`QDRANT_ENABLED=true`)

## Container
Build from repository root (compose context):

```bash
docker compose build backend
docker compose up backend redis
```

The image entrypoint is:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Health checks should target `GET /healthz` (load balancer) and `GET /api/v1/health` (API prefix).

## Environment
Copy `.env.example` to `.env` and set production values. Required keys include `SECRET_KEY`, `REDIS_URL`, and CORS origins for your dashboard domain.

In production set `ENVIRONMENT=production` and a strong `SECRET_KEY`. OpenAPI docs (`/docs`, `/redoc`) are disabled when `ENVIRONMENT` is not `development` and `DEBUG=false`.

## Platforms

### Render / Railway
- Build command: `pip install -r backend/requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Attach Redis add-on and set `REDIS_URL`
- Set health check path to `/healthz`

### VPS / Docker
- Use `backend/Dockerfile` with build context at repo root
- Pass `.env` or platform secrets for all backend keys
- Run behind TLS terminator (nginx, Caddy, cloud LB)

## Validation
```bash
python scripts/validate_env.py
python scripts/validate_env.py --check-example
cd backend && REDIS_ENABLED=false python -m pytest tests/ -q
```
