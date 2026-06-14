# Dahlia Tool

Self-hosted web app for caring for and propagating dahlias. See [ARCHITECT.md](ARCHITECT.md) for the full design.
This version is in Dutch. 

One Docker container serves both the API (FastAPI + SQLite) and the web UI (React). All data — the SQLite database and photos — lives in a single `data/` folder, so a backup is one folder copy.

> **Status: complete (Phases 1–7).** Varieties (with Wikipedia import); plants with `SSDDD` numbering, five origins (incl. provisional "unknown" plants you can name and assign a variety later); the full family tree; inventory counts; photos; locations and plantings with multi-year history; seasonal care tips; winter rest (lifting, eye-status, storage boxes, gated season rollover); per-plant logbook, disposal (discard / give-away / "did not come up"), disease warnings with sibling highlighting, descendant tallies; and insights — per-plant yearly performance and an end-of-season "best spot" ranking with adjustable weights.

## Run with Docker (recommended)

```bash
docker compose up --build
```

Then open <http://localhost:8000>. Data is stored in `./data`.

## Deploy to a server (Proxmox LXC or via SSH)

See **[docs/DEPLOY.md](docs/DEPLOY.md)** for step-by-step install on a Proxmox
container — both a native `systemd` install (`deploy/install.sh`, recommended for an
LXC) and a Docker install.

## Local development

Run the backend and frontend separately for hot-reload. The Vite dev server proxies `/api` to the backend.

**Backend** (Python 3.12+):

```bash
cd backend
python -m venv .venv
# Windows:  .venv\Scripts\activate
# macOS/Linux:  source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000
```

**Frontend** (Node 22+), in a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the URL Vite prints (default <http://localhost:5173>).

## Tests

```bash
cd backend
pytest
```

## Configuration

| Env var      | Default        | Purpose                                  |
|--------------|----------------|------------------------------------------|
| `DATA_DIR`   | `data`         | Folder for the SQLite DB and photos.     |
| `STATIC_DIR` | `app/static`   | Built frontend (set automatically in Docker). |

## Publishing

Pushing to `main` (or a `v*` tag) triggers [.github/workflows/build.yml](.github/workflows/build.yml), which builds the image and pushes it to GitHub Container Registry at `ghcr.io/<owner>/<repo>`. To run that image, set `image:` in [docker-compose.yml](docker-compose.yml) and remove `build:`.
