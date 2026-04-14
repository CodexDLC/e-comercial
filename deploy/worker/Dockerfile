# === STAGE 1: Builder ===
FROM python:3.13-slim AS builder
WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src

RUN python -m venv /app/.venv && \
    /app/.venv/bin/pip install --upgrade pip && \
    /app/.venv/bin/pip install --no-cache-dir .

# === STAGE 2: Runtime ===
FROM python:3.13-slim
WORKDIR /app
RUN useradd -m -u 1000 appuser
COPY --from=builder /app/.venv /app/.venv

COPY src/workers /app/src/workers
COPY src/Hop-and-Barley /app/src/Hop-and-Barley

RUN mkdir -p /app/logs && chown -R appuser:appuser /app

USER appuser
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app:$PYTHONPATH"
