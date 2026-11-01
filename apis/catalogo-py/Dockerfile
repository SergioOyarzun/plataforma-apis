# ---------- Etapa 1: construir ----------
FROM python:3.13-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Primero solo las dependencias: esta capa se reutiliza mientras no cambien
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

# Después el código
COPY app ./app

# ---------- Etapa 2: ejecutar ----------
FROM python:3.13-slim

RUN useradd --uid 10001 --no-create-home app \
 && pip uninstall -y pip setuptools wheel



WORKDIR /app
COPY --from=builder /app /app

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

USER 10001
EXPOSE 8000
CMD ["fastapi", "run", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]
