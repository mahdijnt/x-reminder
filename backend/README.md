# Backend (FastAPI)

## Run locally

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Start Redis for full health (`ok`); without Redis the API still starts and health reports `degraded` with `checks.redis.status=unavailable`. Configure via `REDIS_URL` (supports `redis://` and `rediss://`) and related vars in the repo root `.env.example`.

## Endpoints

- `GET /api/v1/health` — versioned health check (includes Redis ping)
- `GET /healthz` — legacy/simple probe
- `GET /docs` — OpenAPI UI
