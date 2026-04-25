# syntax=docker/dockerfile:1
# uv in Docker: https://docs.astral.sh/uv/guides/integration/docker/
# uv install (standalone): https://docs.astral.sh/uv/getting-started/installation/

FROM python:3.14-slim-trixie

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NO_DEV=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project

COPY server.py ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

# MCP stdio server: attach stdin/stdout when you run the container (see README).
CMD ["uv", "run", "server.py"]
