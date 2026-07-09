# Dashboard Deployment Guide

## Runtime
- Node.js 20+
- Next.js 14 (`next build` / `next start` or Vercel)

## Environment
Set at build time (public) and runtime:

| Variable | Purpose |
| --- | --- |
| `NEXT_PUBLIC_API_BASE_URL` | Backend API base including `/api/v1` |
| `NEXT_PUBLIC_APP_URL` | Canonical dashboard URL (auth redirects, metadata) |
| `NEXT_PUBLIC_USE_MOCK_API` | Set `false` in production |

Validate locally:

```bash
npm run validate:env
```

The script loads repo-root `.env` / `.env.local` when present.

## Vercel
- **Root directory:** `dashboard`
- **Framework preset:** Next.js 14
- **Build command:** `npm run build`
- **Output:** default Next.js (no static export); middleware is supported
- **Env vars:** add `NEXT_PUBLIC_*` values in Vercel project settings for Production and Preview
- Point `NEXT_PUBLIC_API_BASE_URL` to your deployed backend HTTPS origin

## Docker
Build from repository root:

```bash
docker compose build dashboard
```

Requires backend reachable at `NEXT_PUBLIC_API_BASE_URL`.

## Validation
```bash
npm run lint
npm run build
```
