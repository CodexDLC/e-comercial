# === STAGE 1: Builder ===
FROM python:3.13-slim AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc g++ libpq-dev && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
RUN mkdir -p src/Hop-and-Barley && touch src/Hop-and-Barley/__init__.py

RUN python -m venv /venv && \
    /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install --no-cache-dir .

COPY src ./src
RUN /venv/bin/pip install --no-cache-dir .

# === STAGE 2: Runtime ===
FROM python:3.13-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 curl procps && rm -rf /var/lib/apt/lists/* && \
    useradd -m -u 1000 appuser

COPY --from=builder /venv /venv
COPY src/Hop-and-Barley /app
COPY deploy/backend/entrypoint.sh /entrypoint.sh

RUN mkdir -p /app/staticfiles /app/media /app/logs/backend && \
    chown -R appuser:appuser /app && \
    chmod -R 755 /app/media /app/logs/backend && \
    chmod +x /entrypoint.sh

USER appuser

ENV PATH="/venv/bin:$PATH"
ENV PYTHONPATH="/app"
ENV DJANGO_SETTINGS_MODULE="core.settings.dev"

HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl -fL http://localhost:8000/api/v1/health/ || exit 1

WORKDIR /app
ENTRYPOINT ["/entrypoint.sh"]
