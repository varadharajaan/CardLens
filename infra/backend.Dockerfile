# CardLens backend image. Build context = repo root.
FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
WORKDIR /app/backend
ENV PYTHONPATH=/app/backend CARDLENS_ENV=prod
EXPOSE 8000

# Apply migrations, then serve. SQLite (default) is ephemeral; set CARDLENS_DATABASE_URL for Postgres.
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
