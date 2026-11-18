# syntax=docker/dockerfile:1

# =============================================================================
# SafeSite Vision - CPU inference image
#
# Build:  docker build -t safesite-vision .
# Run:    docker run -p 8000:8000 safesite-vision
# =============================================================================

# -----------------------------------------------------------------------------
# Builder: resolve and install the runtime dependency set with uv
# -----------------------------------------------------------------------------
FROM python:3.15-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:0.13.9 /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Layer 1: dependencies only. Copying just the manifests means this layer is
# cached until pyproject.toml or uv.lock actually change.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-default-groups --group app

# Layer 2: the project itself.
COPY pyproject.toml uv.lock README.md ./
COPY src ./src
COPY app ./app
COPY configs ./configs

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-editable --no-default-groups --group app

# -----------------------------------------------------------------------------
# Runtime: slim image, non-root user, no build toolchain
# -----------------------------------------------------------------------------
FROM python:3.15-slim AS runtime

LABEL org.opencontainers.image.title="SafeSite Vision" \
      org.opencontainers.image.description="PPE detection and safety compliance API" \
      org.opencontainers.image.source="https://github.com/MahdiMashayekhi-AI/Safesite-Vision"

RUN groupadd --system --gid 1001 safesite \
    && useradd --system --uid 1001 --gid safesite --create-home --shell /usr/sbin/nologin safesite

WORKDIR /app

COPY --from=builder --chown=safesite:safesite /app /app

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1

USER safesite

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)"

CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]
