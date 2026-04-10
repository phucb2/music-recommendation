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

Set **`BACKEND_API_URL`** (e.g. in `frontend/.env.local`) to `http://localhost:8000` so server-rendered catalog/recommendation calls hit the API. **Analytics persistence:** the browser posts to Next `POST /api/events`, which **forwards** to **`POST {BACKEND_API_URL}/v1/events`**; **only the FastAPI service inserts into Postgres** (`analytics_events`). If `BACKEND_API_URL` is unset, `POST /api/events` returns **503** (no DB write). Catalog pages still fall back to the mock catalog when the API is unavailable.

## Backend (FastAPI + Postgres)

From the repository root with Docker:

```bash
docker compose up --build
```

- **API:** [http://localhost:8000](http://localhost:8000) (OpenAPI: `/docs`)
- **Web:** port **3000** (with `BACKEND_API_URL=http://api:8000` inside Compose)

Local API without Docker: install Python 3.12+, create a venv, `pip install -r backend/requirements.txt`, run Postgres (or point `DATABASE_URL` at a local instance), then:

```bash
cd backend
export DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/music
export CORS_ORIGINS=http://localhost:3000
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Docker (full stack)

From the repository root:

```bash
docker compose build
docker compose up
```

Services: **db** (Postgres 16), **api** (migrations + seed on start), **web** (Next.js). The web container talks to the API over the Compose network.

## Layout

| Location      | Contents                                      |
|---------------|-----------------------------------------------|
| `./`          | Markdown specs, this README                   |
| `./backend/`  | FastAPI app, SQLAlchemy models, Alembic migrations |
| `./frontend/` | Next.js app (`app/`, `components/`, …)        |
