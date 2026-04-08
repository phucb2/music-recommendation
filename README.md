# Music recommendation — docs & demo app

**What:** Repo layout, how to run the Next.js app and Docker.  
**When:** Cloning the repo or onboarding contributors.

Product specs stay in the **repository root** (`mockup.md`, `prd.md`). The **Next.js app** is in [`frontend/`](frontend/).

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

## Docker

From the repository root:

```bash
docker compose build
docker compose up
```

The app is served on port **3000**.

## Layout

| Location    | Contents                          |
|------------|------------------------------------|
| `./`       | Markdown specs, this README        |
| `./frontend/` | Next.js app (`app/`, `components/`, …) |
