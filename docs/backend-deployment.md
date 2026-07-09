# Backend Deployment Guide

## Runtime
- Python 3.11
- Redis required
- Qdrant optional (`QDRANT_ENABLED=true`)

## Steps
1. Build container with `backend/Dockerfile`.
2. Configure production env vars from `.env.example`.
3. Run `uvicorn app.main:app --host 0.0.0.0 --port 8000`.
4. Attach health checks to `/healthz`.
