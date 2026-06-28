# Deployment Guide

Local dev is unchanged: `docker compose up` still works exactly as before.

For production, the stack is split:
- **Frontend** → Vercel (free, always-on)
- **Backend** → Render (free tier, sleeps after 15 min of inactivity — ~30s cold start)
- **PostgreSQL** → Render managed Postgres (free, 90-day expiry then must recreate)
- **ChromaDB** → embedded in the backend container (ephemeral on free tier — data resets on redeploy)

---

## 1. Deploy the backend to Render

### Option A — Blueprint (one click, recommended)

1. Push the `Leo-Agent/` repo to GitHub.
2. Go to [render.com](https://render.com) → **New** → **Blueprint**.
3. Connect your GitHub repo. Render will detect `render.yaml` and create:
   - `zatoona-backend` web service
   - `zatoona-db` PostgreSQL database
4. In the Render dashboard, set the **secret env vars** that have `sync: false` in `render.yaml`:
   - `OPENAI_API_KEY`
   - `GROQ_API_KEY`
   - `LIGHTNING_API_KEY`
   - `LIGHTNING_MODEL_NAME`
5. Click **Apply**. First deploy takes ~10–15 minutes (pip installs + ML model downloads).
6. Copy the backend URL from the Render dashboard (e.g. `https://zatoona-backend.onrender.com`).

### Option B — Manual

1. **New → PostgreSQL** → name: `zatoona-db`, plan: Free → Create.
2. **New → Web Service** → connect repo, select `Leo-Agent/` as root.
   - Runtime: Docker
   - Dockerfile path: `./Dockerfile.app`
   - Plan: Free
3. Add all env vars from `render.yaml` manually, plus `DATABASE_URL` from step 1's connection string.
4. Deploy.

---

## 2. Deploy the frontend to Vercel

1. Go to [vercel.com](https://vercel.com) → **New Project** → import your repo.
2. Set **Root Directory** to `Leo-Agent/zatoona-web`.
3. Add one environment variable:
   - `VITE_API_BASE` = `https://zatoona-backend.onrender.com` (your Render URL from step 1)
4. Deploy. Vercel auto-detects Vite and uses `vercel.json` for SPA routing.

---

## 3. Verify

- Open the Vercel URL → login/signup should work.
- First request after the backend has been idle will be slow (~30s) — this is the Render free tier cold start.
- Upload notes, generate an exam, submit answers.

---

## Limitations of the free tier

| Thing | Behaviour |
|---|---|
| Backend cold start | ~30–60s after 15 min of no traffic |
| ChromaDB data | Lost on every Render redeploy (acceptable for demo) |
| PostgreSQL | Free for 90 days, then Render deletes it — recreate and redeploy |
| Concurrent requests | Limited by Render's single free instance |

---

## Local dev (unchanged)

```bash
cd Leo-Agent
docker compose up
```

Frontend dev server (in a separate terminal):

```bash
cd Leo-Agent/zatoona-web
npm install
npm run dev        # proxies API calls to localhost:80 (nginx)
```
