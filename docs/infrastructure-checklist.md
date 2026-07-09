# Infrastructure Checklist

## Secrets
- [ ] `SECRET_KEY` is unique per environment (not example placeholders)
- [ ] `TELEGRAM_BOT_TOKEN` stored only in secret manager / platform env
- [ ] X OAuth client secret and optional `X_TOKEN_ENCRYPTION_KEY` set
- [ ] No secrets committed to git (`.env` gitignored)

## Redis
- [ ] `REDIS_URL` set and reachable
- [ ] persistence/backup strategy enabled

## Qdrant (optional)
- [ ] `QDRANT_URL` configured when `QDRANT_ENABLED=true`
- [ ] API key set if cluster is secured

## API
- [ ] `ENVIRONMENT=production`
- [ ] `CORS_ORIGINS` lists only trusted dashboard origins (HTTPS)
- [ ] Health checks: `/healthz` and `/api/v1/health`
- [ ] TLS terminated at edge (HSTS enabled in production responses)

## Dashboard
- [ ] `NEXT_PUBLIC_USE_MOCK_API=false`
- [ ] `NEXT_PUBLIC_API_BASE_URL` points to production API
- [ ] Vercel env vars set for Production and Preview as needed

## X API
- [ ] OAuth keys/secrets configured
- [ ] callback URL matches deployed backend (`X_CALLBACK_URL`)

## CI/CD
- [ ] `backend-ci`, `dashboard-ci`, `telegram-bot-ci` passing on default branch
- [ ] Weekly `security-audit` workflow reviewed
