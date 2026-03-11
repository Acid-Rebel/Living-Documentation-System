# DevOps Documentation — Living Documentation System

> **Live URL:** [https://docswiki.dev](https://docswiki.dev)  
> **Backend:** Heroku (Python 3.12 / FastAPI / Uvicorn)  
> **Frontend:** Vercel (Next.js 15 / TypeScript)  
> **Custom Domain:** `docswiki.dev` → Vercel | `api.docswiki.dev` (or Heroku app URL) → Heroku

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Infrastructure](#2-infrastructure)
3. [Environment Variables](#3-environment-variables)
4. [Heroku — Backend Deployment](#4-heroku--backend-deployment)
5. [Vercel — Frontend Deployment](#5-vercel--frontend-deployment)
6. [Custom Domain Setup](#6-custom-domain-setup)
7. [CI/CD Pipeline](#7-cicd-pipeline)
8. [Monitoring & Logging](#8-monitoring--logging)
9. [Rollback Procedures](#9-rollback-procedures)
10. [Troubleshooting](#10-troubleshooting)
11. [Security Checklist](#11-security-checklist)

---

## 1. Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│                     User Browser                         │
│               https://docswiki.dev                       │
└───────────────────────┬──────────────────────────────────┘
                        │ HTTPS (443)
                        ▼
┌───────────────────────────────────────┐
│              Vercel Edge Network       │
│  Next.js 15 (SSR + Static)            │
│  custom domain: docswiki.dev          │
│                                       │
│  API Rewrites (next.config.ts):       │
│  /api/*  →  Heroku Backend            │
│  /export/* → Heroku Backend           │
└───────────────────────┬───────────────┘
                        │ HTTPS → SERVER_BASE_URL
                        ▼
┌───────────────────────────────────────┐
│           Heroku Dyno (Web)            │
│  Python 3.12 / FastAPI / Uvicorn      │
│  Entry: python -m core.main           │
│  Port: $PORT (set by Heroku)          │
│                                       │
│  Apt packages: git                    │
│  Buildpack: heroku/python             │
└───────────────────────────────────────┘
```

### Key Design Points

| Concern | Decision |
|---|---|
| API proxying | Next.js rewrites forward `/api/lds/*`, `/api/wiki_cache/*`, `/export/wiki/*`, `/api/auth/*`, `/api/lang/*` to the Heroku backend — no CORS issues |
| Zero-config deploys | `git push heroku main` triggers automatic build + restart |
| Secrets management | Heroku Config Vars (backend) + Vercel Environment Variables (frontend) — never committed to git |
| Python version | Pinned to `3.12` via `.python-version` |

---

## 2. Infrastructure

### Components

| Component | Platform | Region | Plan |
|---|---|---|---|
| Backend API | Heroku | (your region) | Eco / Basic Dyno |
| Frontend Web | Vercel | Global Edge | Hobby / Pro |
| DNS | (your registrar) | — | — |

### Networking

- **Frontend → Backend**: All API calls are routed through Next.js rewrites on the Vercel server, so the browser never directly contacts Heroku. This eliminates CORS configuration requirements.
- **Port binding**: Heroku dynamically assigns `$PORT`. `core/main.py` reads `os.environ.get("PORT", 8001)` to bind correctly.
- **TLS**: Both Heroku and Vercel provide automatic TLS for custom domains (ACM / Vercel managed certificates).

---

## 3. Environment Variables

### Backend (Heroku Config Vars)

Set via Heroku Dashboard → **Settings → Config Vars**, or via CLI:

```bash
heroku config:set KEY=VALUE --app <your-heroku-app-name>
```

| Variable | Required | Description |
|---|---|---|
| `GOOGLE_API_KEY` | ✅ Yes | Google Gemini API key |
| `OPENAI_API_KEY` | Optional | OpenAI API key |
| `OPENROUTER_API_KEY` | Optional | OpenRouter API key |
| `AWS_ACCESS_KEY_ID` | Optional | AWS Bedrock key |
| `AWS_SECRET_ACCESS_KEY` | Optional | AWS Bedrock secret |
| `AWS_SESSION_TOKEN` | Optional | AWS Bedrock session token |
| `AWS_REGION` | Optional | AWS region for Bedrock |
| `AWS_ROLE_ARN` | Optional | AWS IAM Role ARN |
| `DEEPWIKI_AUTH_MODE` | Optional | Enable auth (`true`/`false`, default: `false`) |
| `DEEPWIKI_AUTH_CODE` | Optional | Auth code when auth mode enabled |
| `DEEPWIKI_EMBEDDER_TYPE` | Optional | `openai`, `google`, `bedrock`, `ollama` (default: `openai`) |
| `DEEPWIKI_CONFIG_DIR` | Optional | Override config directory path |
| `NODE_ENV` | Optional | Set to `production` to disable hot-reload |

> **Tip:** `NODE_ENV=production` disables the watchfiles dev reload loop on Heroku, preventing unnecessary CPU usage.

### Frontend (Vercel Environment Variables)

Set via Vercel Dashboard → **Project → Settings → Environment Variables**:

| Variable | Required | Description |
|---|---|---|
| `SERVER_BASE_URL` | ✅ Yes | Full Heroku backend URL, e.g., `https://<your-app>.herokuapp.com` |

All frontend API routing depends on `SERVER_BASE_URL` being correctly set. Without it, rewrites fall back to `http://localhost:8001` (development only).

---

## 4. Heroku — Backend Deployment

### One-Time Setup

```bash
# Install Heroku CLI and login
heroku login

# Create the app (if not already created)
heroku create <your-app-name>

# Add the Python buildpack
heroku buildpacks:set heroku/python --app <your-app-name>

# Link your local git repo to the Heroku remote
heroku git:remote -a <your-app-name>
```

### Key Configuration Files

| File | Purpose |
|---|---|
| `Procfile` | Defines the dyno process: `web: python -m core.main` |
| `Aptfile` | Installs system-level apt packages: `git` |
| `.python-version` | Pins Python runtime to `3.12` |
| `requirements.txt` | Python dependencies installed during slug compilation |

### Deploy

```bash
# Push from main branch to Heroku
git push heroku main

# Push a different local branch to Heroku main (e.g., feature branch)
git push heroku feat/my-feature:main
```

### Useful Heroku CLI Commands

```bash
# View live logs (streaming)
heroku logs --tail --app <your-app-name>

# View last 200 log lines
heroku logs -n 200 --app <your-app-name>

# Check dyno status
heroku ps --app <your-app-name>

# Restart all dynos (force restart)
heroku restart --app <your-app-name>

# Open a one-off bash shell on Heroku
heroku run bash --app <your-app-name>

# List all config vars
heroku config --app <your-app-name>

# Scale dynos
heroku ps:scale web=1 --app <your-app-name>
```

### Slug Compilation Steps (Heroku Build Lifecycle)

1. Heroku detects `Aptfile` → installs `git` via apt
2. Heroku detects `.python-version` → provisions Python 3.12 runtime
3. `pip install -r requirements.txt` runs to install Python dependencies
4. Dyno starts: `python -m core.main` as defined in `Procfile`
5. `core/main.py` binds Uvicorn to `0.0.0.0:$PORT`

### Heroku Dyno Sleep Policy (Eco Plan)

On the **Eco plan**, dynos sleep after 30 min of inactivity. To prevent this:
- Upgrade to **Basic** or higher dyno
- Use an uptime monitoring service (e.g., UptimeRobot to ping `https://<your-app>.herokuapp.com/` every 25 min)

---

## 5. Vercel — Frontend Deployment

### One-Time Setup

1. Push the repository to GitHub
2. Go to [vercel.com](https://vercel.com) → **Add New Project**
3. Import the GitHub repository
4. Set **Root Directory** to `frontend`
5. Framework preset: **Next.js** (auto-detected)
6. Add `SERVER_BASE_URL` environment variable
7. Click **Deploy**

### Automatic Deployments

Vercel automatically deploys on every push to the linked GitHub branch (typically `main`). Pull requests get **preview deployments** with unique URLs.

| Event | Behavior |
|---|---|
| Push to `main` | Production deployment to `docswiki.dev` |
| Pull Request opened | Preview deployment (unique URL) |
| Push to other branches | Preview deployment |

### Manual Deploy via Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy from the frontend directory
cd frontend
vercel --prod
```

### Build Configuration (`frontend/next.config.ts`)

The Next.js config sets up server-side API rewrites so all `/api/*`, `/export/*`, and other backend routes are proxied to `SERVER_BASE_URL`:

```
/api/wiki_cache/*  →  ${SERVER_BASE_URL}/api/wiki_cache/*
/export/wiki/*     →  ${SERVER_BASE_URL}/export/wiki/*
/api/auth/status   →  ${SERVER_BASE_URL}/auth/status
/api/auth/validate →  ${SERVER_BASE_URL}/auth/validate
/api/lang/config   →  ${SERVER_BASE_URL}/lang/config
/api/lds/*         →  ${SERVER_BASE_URL}/api/lds/*
/local_repo/structure → ${SERVER_BASE_URL}/local_repo/structure
```

> **Important:** These rewrites execute on the **Vercel server**, not in the browser. `SERVER_BASE_URL` must be set as a **server-side** environment variable (not `NEXT_PUBLIC_`).

---

## 6. Custom Domain Setup

### Domain: `docswiki.dev`

#### Step 1 — Add Domain in Vercel

1. Vercel Dashboard → Project → **Settings → Domains**
2. Add `docswiki.dev` and `www.docswiki.dev`
3. Vercel will display DNS records to configure

#### Step 2 — Configure DNS at Your Registrar

For the apex domain (`docswiki.dev`):

| Type | Name | Value |
|---|---|---|
| `A` | `@` | `76.76.21.21` *(Vercel IP — verify in Vercel dashboard)* |

For `www` subdomain:

| Type | Name | Value |
|---|---|---|
| `CNAME` | `www` | `cname.vercel-dns.com` |

#### Step 3 — TLS Certificate

Vercel automatically provisions a free TLS certificate via Let's Encrypt. DNS propagation can take up to 48 hours.

#### Backend Domain (Optional)

If you want the backend to be accessible on a subdomain (e.g., `api.docswiki.dev`):

1. Add `api.docswiki.dev` custom domain in Heroku:
   ```bash
   heroku domains:add api.docswiki.dev --app <your-app-name>
   ```
2. Heroku will provide a DNS target. Add a CNAME at your registrar:

| Type | Name | Value |
|---|---|---|
| `CNAME` | `api` | `<heroku-dns-target>.herokudns.com` |

3. Update `SERVER_BASE_URL` in Vercel to `https://api.docswiki.dev`

---

## 7. CI/CD Pipeline

### GitHub Actions: `python-tests.yml`

Located at `.github/workflows/python-tests.yml`. Triggers on:
- Push to `main` or any `feat/*` branch
- Pull requests targeting `main`

**Pipeline Steps:**

```
Push / PR → GitHub Actions → Ubuntu Runner
  ├── actions/checkout@v3
  ├── Setup Python 3.10
  ├── pip install dependencies
  └── pytest tests/ --cov=./ --cov-report=xml
        └── Upload coverage to Codecov
```

> **Note:** The workflow uses Python 3.10 for testing while the Heroku deployment runs Python 3.12. Consider aligning these.

### Recommended: Add Heroku + Vercel Auto-Deploy

**Current state:** Deployments are triggered manually via `git push heroku main`.

**Recommended enhancement** — Add a deploy step to GitHub Actions after tests pass:

```yaml
# .github/workflows/deploy.yml (example)
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    needs: test  # only deploy if tests pass
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
      - uses: akhileshns/heroku-deploy@v3.13.15
        with:
          heroku_api_key: ${{ secrets.HEROKU_API_KEY }}
          heroku_app_name: ${{ secrets.HEROKU_APP_NAME }}
          heroku_email: ${{ secrets.HEROKU_EMAIL }}
```

Vercel auto-deploys via GitHub integration — no extra workflow needed.

### Required GitHub Secrets

| Secret | Used By |
|---|---|
| `HEROKU_API_KEY` | Heroku deploy action |
| `HEROKU_APP_NAME` | Heroku deploy action |
| `HEROKU_EMAIL` | Heroku deploy action |
| `GEMINI_API_KEY` | Test runs (if integration tests needed) |
| `OPENAI_API_KEY` | Test runs (if integration tests needed) |

Set secrets in GitHub → **Repository → Settings → Secrets and variables → Actions**.

---

## 8. Monitoring & Logging

### Heroku Logs

```bash
# Stream live logs
heroku logs --tail --app <your-app-name>

# Filter by dyno type
heroku logs --tail --dyno web --app <your-app-name>
```

Log format example:
```
2026-03-11T04:30:00Z app[web.1]: INFO:     Application startup complete.
2026-03-11T04:30:01Z app[web.1]: INFO:     Started server process [4]
2026-03-11T04:30:05Z heroku[router]: at=info method=GET path="/api/lds/..."
```

### Application Logging

The backend uses structured logging configured in `core/logging_config.py`. Log output is directed to stdout/stderr, which Heroku captures automatically.

### Vercel Analytics

Enable **Vercel Analytics** in the Vercel Dashboard for:
- Page views and Web Vitals
- Real-user performance data
- Error tracking

### Uptime Monitoring (Recommended)

Use a free service like [UptimeRobot](https://uptimerobot.com) or [Better Stack](https://betterstack.com) to:
- Monitor `https://docswiki.dev` (frontend)
- Monitor `https://<your-app>.herokuapp.com/` or `https://api.docswiki.dev/` (backend health)
- Alert on downtime via email/Slack

### Health Check Endpoint (Recommended)

Add a `/health` endpoint to `core/api.py` for Heroku and uptime monitors:

```python
@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}
```

---

## 9. Rollback Procedures

### Backend Rollback (Heroku)

Heroku retains previous slugs. Roll back instantly via dashboard or CLI:

```bash
# List previous releases
heroku releases --app <your-app-name>

# Roll back to a specific version (e.g., v42)
heroku rollback v42 --app <your-app-name>
```

### Frontend Rollback (Vercel)

1. Go to Vercel Dashboard → Project → **Deployments**
2. Find the last good deployment
3. Click the **⋯ menu** → **Promote to Production**

Or via CLI:
```bash
vercel rollback --app <your-project-name>
```

---

## 10. Troubleshooting

### Backend Issues

| Symptom | Likely Cause | Fix |
|---|---|---|
| `H10 App crashed` in Heroku logs | Python import error or missing env var | Run `heroku logs --tail` to see the traceback |
| `H14 No web dynos running` | Dyno is down (0 dynos scaled) | `heroku ps:scale web=1` |
| `R10 Boot timeout` | App takes >60s to start | Reduce startup time; lazy-load heavy models |
| `Missing environment variable: GOOGLE_API_KEY` warning | Config var not set | `heroku config:set GOOGLE_API_KEY=...` |
| App works locally but fails on Heroku | Missing dependency in `requirements.txt` | Add the missing package and redeploy |
| Slow response / timeouts on Eco plan | Dyno sleep | Upgrade to Basic dyno or add uptime pinger |

### Frontend Issues

| Symptom | Likely Cause | Fix |
|---|---|---|
| API calls return 500/failed | `SERVER_BASE_URL` not set or Heroku dyno sleeping | Check Vercel env vars; wake Heroku dyno |
| Build fails on Vercel | TypeScript or ESLint errors | Run `cd frontend && yarn build` locally first |
| Domain shows Vercel 404 | DNS not propagated or misconfigured | Check DNS records; wait up to 48h |
| WebSocket connection failing | `wss://` not proxied via rewrites | WebSockets need direct URL, not Next.js rewrites |

### Local Development (Reference)

```bash
# Backend
cd Living-Documentation-System
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m core.main

# Frontend
cd frontend
yarn install
yarn dev  # http://localhost:3000
```

Make sure `.env` at project root contains at minimum:
```
GOOGLE_API_KEY=your-key-here
```

---

## 11. Security Checklist

- [ ] `.env` is listed in `.gitignore` (never committed)
- [ ] All API keys stored in Heroku Config Vars / Vercel Environment Variables
- [ ] `DEEPWIKI_AUTH_MODE=true` and `DEEPWIKI_AUTH_CODE` set if wiki should be access-controlled
- [ ] Heroku app uses HTTPS only (enforce via `heroku config:set FORCE_SSL=true` if needed)
- [ ] Vercel enforces HTTPS automatically
- [ ] Sensitive GitHub Secrets added (not hardcoded in workflow files)
- [ ] `requirements.txt` pinned to specific versions (prevents supply-chain drift)
- [ ] Codecov integration in place for test coverage visibility
- [ ] Regular dependency updates reviewed (Dependabot or manual audit)

---

## Quick Reference

```bash
# Deploy backend
git push heroku main

# Stream backend logs
heroku logs --tail --app <your-app-name>

# Rollback backend
heroku rollback v<N> --app <your-app-name>

# Set a backend env var
heroku config:set KEY=VALUE --app <your-app-name>

# Scale dynos
heroku ps:scale web=1 --app <your-app-name>

# Deploy frontend (manual)
cd frontend && vercel --prod

# Run tests locally
pytest tests/ --cov=./ -v
```

---

*Last updated: 2026-03-11 | Maintained by the Living Documentation System team*
