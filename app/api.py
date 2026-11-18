"""FastAPI service exposing SafeSite Vision violation events.

Run locally:
    uv run uvicorn app.api:app --reload --port 8000

The container image in ``Dockerfile`` exposes the same app.
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI

from safesite import __version__

app = FastAPI(
    title="SafeSite Vision API",
    description="PPE detection and safety-compliance violation events.",
    version=__version__,
)


@app.get("/health", tags=["ops"])
def health() -> dict[str, str]:
    """Liveness probe used by the container healthcheck and by CI smoke tests."""
    return {"status": "ok", "version": __version__}


@app.get("/events", tags=["events"])
def list_events() -> list[dict[str, Any]]:
    """Return the violation events detected so far.

    TODO(phase-5): stream events produced by :class:`safesite.pipeline.CompliancePipeline`.
    """
    return []
