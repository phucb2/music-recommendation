# Music recommendation — docs & demo app

**What:** Repo layout, how to run the Next.js app, API, Postgres, and Docker.  
**When:** Cloning the repo or onboarding contributors.

Product specs stay in the **repository root** (`mockup.md`, `prd.md`). The **Next.js app** is in [`frontend/`](frontend/). The **catalog + analytics API** is in [`backend/`](backend/).

## Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

```bash
npm run build   # production build
npm run start   # run production server locally
npm run lint
```

Put **`BACKEND_API_URL`** (and any Supabase keys you use in the browser) in **`.env.local` at the repository root** — Next.js loads it via [`frontend/next.config.mjs`](frontend/next.config.mjs) (`loadEnvConfig` on the repo root). Point **`BACKEND_API_URL`** at `http://localhost:8000` when the API runs locally. **Analytics persistence:** the browser posts to Next `POST /api/events`, which **forwards** to **`POST {BACKEND_API_URL}/v1/events`**; **only the FastAPI service inserts into Postgres** (`analytics_events`). If `BACKEND_API_URL` is unset, `POST /api/events` returns **503** (no DB write). Catalog pages still fall back to the mock catalog when the API is unavailable.

## Backend (FastAPI + Prisma + Supabase Postgres)

The default database is **Supabase** (hosted Postgres). Prisma uses **`DATABASE_URL`** (pooled, for the app) and **`DIRECT_URL`** (direct, for migrations) from the Supabase project settings.

Copy [`.env.local.example`](.env.local.example) to **`.env.local`** at the repo root and fill in both URLs. Password characters like `&`, `#`, and `?` must be **percent-encoded** in the URL.

### Docker (recommended): API + web → Supabase

From the repository root (requires **`.env.local`** with `DATABASE_URL` and `DIRECT_URL`):

```bash
docker compose up --build
```

- **API:** [http://localhost:8000](http://localhost:8000) (OpenAPI: `/docs`) — on start it runs **`prisma migrate deploy`** then **seed** against Supabase.
- **Web:** [http://localhost:3000](http://localhost:3000) — talks to the API as `http://api:8000` inside Compose; your browser still uses **`BACKEND_API_URL=http://localhost:8000`** from `.env.local` for server-side Next fetches where applicable.

There is **no Postgres container** in the default stack; the API connects to Supabase over the public network.

### Optional: Docker + local Postgres (no Supabase)

If you need a self-contained DB (e.g. offline):

```bash
docker compose -f docker-compose.yml -f docker-compose.localdb.yml up --build
```

Set **`.env.local`** to use the Compose service **`db`** (same value for both URLs), for example:

`DATABASE_URL=postgresql://postgres:postgres@db:5432/music`  
`DIRECT_URL=postgresql://postgres:postgres@db:5432/music`

### Migrate tables + seed data to Supabase (CLI)

From **`backend/`** with dependencies installed (`pip install -r requirements.txt`) and **Supabase** URLs in repo-root **`.env.local`**:

```bash
cd backend
python -m scripts.migrate_supabase
```

This runs **`prisma migrate deploy`**, **`prisma generate`**, and **`python -m app.seed`**. It **refuses** `DATABASE_URL` / `DIRECT_URL` that look like **localhost**, **127.0.0.1**, **`@db:`**, or **`host.docker.internal`** (so you do not accidentally migrate a local DB). To allow those anyway (e.g. optional Docker Postgres overlay), set **`ALLOW_LOCAL_MIGRATE=1`**.

### Local API without Docker

Install Python 3.12+, a venv, and `pip install -r backend/requirements.txt`, then:

```bash
cd backend
python -m scripts.migrate_supabase   # once: schema + seed on Supabase
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

For **optional Docker Postgres** instead of Supabase, use the compose overlay and set **`ALLOW_LOCAL_MIGRATE=1`** when running **`python -m scripts.migrate_supabase`**, or use plain **`python -m prisma migrate deploy`** and **`python -m app.seed`** with local URLs in **`.env.local`**.

### Moving data from old local Postgres into Supabase

1. **Schema:** apply migrations on Supabase (`docker compose up`, or **`cd backend && python -m scripts.migrate_supabase`**). Do not run conflicting DDL in the Supabase SQL editor if Prisma already owns the schema.
2. **Rows:** from a machine that can reach **both** databases, dump then restore, for example:

```bash
pg_dump "$OLD_LOCAL_URL" --data-only --no-owner --table=users --table=songs --table=analytics_events > data.sql
psql "$SUPABASE_DIRECT_URL" -f data.sql
```

Adjust tables and flags if your local schema differed. For a fresh Supabase project, **seed** (`python -m app.seed` or API container startup) may be enough.

## Layout

| Location      | Contents                                      |
|---------------|-----------------------------------------------|
| `./`          | Markdown specs, this README                   |
| `./backend/`  | FastAPI app, Prisma schema and migrations (`prisma/`) |
| `./frontend/` | Next.js app (`app/`, `components/`, …)        |
