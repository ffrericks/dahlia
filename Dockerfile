# --- Stage 1: build the frontend ---
FROM node:22-alpine AS frontend
WORKDIR /frontend
COPY frontend/package.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# --- Stage 2: backend + bundled frontend ---
FROM python:3.12-slim AS runtime
WORKDIR /app

COPY backend/pyproject.toml ./
COPY backend/app ./app
# Built frontend lands inside the package so it ships with the installed wheel.
COPY --from=frontend /frontend/dist ./app/static
RUN pip install --no-cache-dir .

# Data volume: SQLite file + photos. Backing up = copying this one folder.
ENV DATA_DIR=/data
VOLUME ["/data"]

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
