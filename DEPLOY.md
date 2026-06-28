# Deployment Guide

Local dev is unchanged: `docker compose up` still works exactly as before.

For production:
- **Frontend** → Vercel (free, always-on)
- **Backend** → Railway ($5 free trial credit, no credit card required — enough for ~1 week demo)
- **PostgreSQL** → Railway managed Postgres (included in the same project, uses trial credit)
- **ChromaDB** → embedded in the backend container (ephemeral — data resets on redeploy, fine for demo)

---

## 1. Deploy the backend to Railway

### Prerequisites
- Push the `Leo-Agent/` repo to GitHub (it already has its own `.git`).
- Sign up at [railway.app](https://railway.app) with GitHub. You get $5 free credit, no card needed.

### Steps

1. **New Project → Deploy from GitHub repo** → select your `Leo-Agent` repo.
   Railway detects `railway.toml` automatically.

2. **Add PostgreSQL**: inside your project, click **+ New** → **Database** → **PostgreSQL**.
   Railway wires up `DATABASE_URL` automatically — no manual copy needed.

3. **Set environment variables** on the backend service (Settings → Variables):

   | Variable | Value |
   |---|---|
   | `OPENAI_API_KEY` | your key |
   | `GROQ_API_KEY` | your key |
   | `GROQ_MODEL` | `llama-3.3-70b-versatile` |
   | `LIGHTNING_API_KEY` | your key |
   | `LIGHTNING_BASE_URL` | `https://lightning.ai/api/v1/` |
   | `LIGHTNING_MODEL_NAME` | your model name |
   | `SECRET_KEY` | any long random string (e.g. run `openssl rand -hex 32`) |
   | `ALGORITHM` | `HS256` |
   | `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` |
   | `REFRESH_TOKEN_EXPIRE_DAYS` | `7` |
   | `EMBEDDING_MODEL` | `text-embedding-3-small` |
   | `CHROMA_PERSIST_DIR` | `/app/chroma_db` |
   | `CHROMA_COLLECTION_NAME` | `student_notes` |
   | `MCP_SERVER_HOST` | `localhost` |
   | `MCP_SERVER_PORT` | `8000` |
   | `RETRIEVAL_TOP_K` | `5` |
   | `RETRIEVAL_MODE` | `hybrid` |
   | `RERANK_ENABLED` | `true` |
   | `RERANKER_MODEL` | `cross-encoder/ms-marco-MiniLM-L-6-v2` |
   | `DOCLING_OCR_ENGINE` | `rapidocr` |
   | `DOCLING_DO_OCR` | `true` |
   | `CHUNK_MODE` | `hybrid` |
   | `CHUNK_MAX_TOKENS` | `512` |
   | `USE_REAL_MCP` | `true` |
   | `USE_REAL_EXAM` | `true` |
   | `USE_REAL_ANSWERS` | `true` |
   | `MAX_VALIDATION_ITERATIONS` | `3` |

4. Railway will build and deploy. First deploy takes ~10–15 min (pip installs + ML model downloads).

5. **Generate a public URL**: Settings → Networking → **Generate Domain**.
   Copy this URL (e.g. `https://zatoona-backend-production.up.railway.app`).

---

## 2. Deploy the frontend to Vercel

1. Go to [vercel.com](https://vercel.com) → **New Project** → import your repo.
2. Set **Root Directory** to `Leo-Agent/zatoona-web`.
3. Add one environment variable:
   - `VITE_API_BASE` = your Railway URL from step 1.5 above
4. Deploy. Vercel auto-detects Vite and uses `vercel.json` for SPA routing.

---

## 3. Verify

- Open the Vercel URL → login/signup → upload notes → generate exam → submit answers.
- First request will be slow the first time (cold build), subsequent ones are fast.

---

## Limitations

| Thing | Behaviour |
|---|---|
| Trial credit | ~1 week of usage for a single service + Postgres; top up with card to extend |
| ChromaDB data | Lost on every Railway redeploy (fine for demo) |
| Concurrent requests | Single Railway instance |

---

## Local dev (unchanged)

```bash
cd Leo-Agent
docker compose up
```

Frontend dev server:
```bash
cd Leo-Agent/zatoona-web
npm install
npm run dev   # proxies API calls to localhost:80 (nginx)
```
