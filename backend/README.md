# Backend (FastAPI)

## Run locally

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Endpoints

- `GET /api/v1/health` — versioned health check
- `GET /healthz` — legacy/simple probe
- `GET /docs` — OpenAPI UI
