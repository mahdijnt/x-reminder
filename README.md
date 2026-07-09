# X Reminder Monorepo

Production-ready monorepo with three applications:
- `backend/` FastAPI API + workers
- `dashboard/` Next.js dashboard
- `telegram-bot/` Telegram bot

## Quick Start

1. Copy `.env.example` to `.env` and fill values.
2. Run backend:
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
3. Run dashboard:
```bash
cd dashboard
npm install
npm run dev
```
4. Run bot:
```bash
cd telegram-bot
pip install -r requirements.txt
python main.py
```

## Production Validation

```bash
python scripts/validate_env.py
python -m compileall backend/app
npm --prefix dashboard run lint
npm --prefix dashboard run build
python -m compileall telegram-bot
```

## Deployment Docs

- `docs/backend-deployment.md`
- `docs/dashboard-deployment.md`
- `docs/telegram-bot-deployment.md`
- `docs/infrastructure-checklist.md`
