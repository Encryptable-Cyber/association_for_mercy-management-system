# ─── Stage 1: Base Python Image ───────────────────────────────
FROM python:3.12-slim

# Prevent Python from writing .pyc files and buffering output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ─── Create Non-Root User ─────────────────────────────────────
RUN groupadd -r mercy && useradd -r -g mercy mercy

# ─── Set Working Directory ────────────────────────────────────
WORKDIR /app

# ─── Install System Dependencies ──────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    gettext \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# ─── Install Python Dependencies ──────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ─── Copy Application Code ────────────────────────────────────
COPY . .

# ─── Entrypoint Script ────────────────────────────────────────
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# ─── Create Directories for Media, Static & Logs ──────────────
RUN mkdir -p /app/media /app/staticfiles /app/sent_emails /app/logs

# ─── Change Ownership to Non-Root User ────────────────────────
RUN chown -R mercy:mercy /app
USER mercy

# ─── Expose Port ──────────────────────────────────────────────
EXPOSE 8000

# ─── Run Application ──────────────────────────────────────────
ENTRYPOINT ["/entrypoint.sh"]
# Production: Gunicorn with Railway's PORT env var (default 8000)
CMD sh -c "gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 3 --timeout 120 config.wsgi:application"