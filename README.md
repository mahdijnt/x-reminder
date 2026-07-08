# X Engagement Intelligence Manager

A monorepo-style starter for an engagement intelligence system.

## Stack
- `dashboard`: Next.js (React + TypeScript)
- `backend`: FastAPI (Python)
- `telegram-bot`: Python Telegram bot (skeleton)

## Getting started
1. Create your environment file:
   - Copy `.env.example` to `.env`.

### Dashboard
```bash
cd dashboard
npm install
npm run dev
```

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Telegram bot
```bash
cd telegram-bot
pip install -r requirements.txt
python main.py
```
