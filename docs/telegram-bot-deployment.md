# Telegram Bot Deployment Guide

## Runtime
- Python 3.11+
- `TELEGRAM_BOT_TOKEN`

## Environment
From `.env.example`:
- `TELEGRAM_BOT_TOKEN`
- `BOT_BACKEND_BASE_URL` (production API `/api/v1` URL)
- `USE_MOCK_BACKEND=false` in production

## Steps
1. Build with `telegram-bot/Dockerfile` (context: repo root) or `pip install -r requirements.txt`.
2. Configure token and backend URL via platform secrets.
3. Run `python main.py` (long-running process).

## Docker Compose
```bash
docker compose up telegram-bot backend redis
```

## Validation
```bash
python -m compileall telegram-bot
python -c "import main"
```
