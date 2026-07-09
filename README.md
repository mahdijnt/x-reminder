# X Reminder Monorepo

Production-oriented monorepo for X (Twitter) engagement tracking and reminders.

| App | Stack | Path |
| --- | --- | --- |
| API | FastAPI + Redis (+ optional Qdrant) | `backend/` |
| Dashboard | Next.js 14 | `dashboard/` |
| Telegram bot | Python | `telegram-bot/` |

## Prerequisites
- Python 3.11+
- Node.js 20+
- Redis (backend and workers)
- Optional: Qdrant for vector features

## Local development
1. Copy `.env.example` to `.env` and adjust values.
2. Start Redis (or `docker compose up redis`).
3. Backend:
   ```bash
   cd backend
   pip install -r requirements.txt
   set REDIS_ENABLED=false   # optional smoke without Redis
   uvicorn app.main:app --reload --port 8000
   ```
4. Dashboard:
   ```bash
   cd dashboard
   npm install
   npm run dev
   ```
5. Telegram bot:
   ```bash
   cd telegram-bot
   pip install -r requirements.txt
   python main.py
   ```

## Production validation (release gate)
Run from repository root:

```bash
python scripts/validate_env.py --check-example
python scripts/validate_env.py
python -m compileall backend/app
cd backend && set REDIS_ENABLED=false&& python -m pytest tests/ -q
npm --prefix dashboard run lint
npm --prefix dashboard run build
python -m compileall telegram-bot
cd telegram-bot && python -c "import main"
```

CI mirrors these checks in `.github/workflows/`.

## Security notes
- Set `ENVIRONMENT=production` and a strong `SECRET_KEY` on the API.
- Dashboard auth tokens are HMAC-signed with `SECRET_KEY`; do not use default secrets in production.
- OpenAPI UI is disabled outside development unless `DEBUG=true`.
- Run scheduled dependency audits via `.github/workflows/security-audit.yml`.

## Deployment
- [Backend (Render/Railway/VPS/Docker)](docs/backend-deployment.md)
- [Dashboard (Vercel/Docker)](docs/dashboard-deployment.md)
- [Telegram bot](docs/telegram-bot-deployment.md)
- [Infrastructure checklist](docs/infrastructure-checklist.md)

## Docker Compose
Full stack from repo root:

```bash
docker compose up --build
```

Services use repo-root `.env` via `env_file`.

## License
See [LICENSE](LICENSE).
