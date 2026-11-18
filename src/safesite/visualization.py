"""Drawing helpers for frames, tracks and violation overlays.

Kept separate from the pipeline so that headless batch jobs do not need any
rendering logic, and so the Streamlit demo can reuse the same primitives.
"""

from __future__ import annotations

from typing import Any

__all__ = ["annotate_frame"]


def annotate_frame(
    frame: Any,
    detections: list[dict[str, Any]] | None = None,
    violations: list[dict[str, Any]] | None = None,
) -> Any:
    """Draw detection boxes, track ids and violation overlays onto ``frame``.

    Args:
        frame: A BGR ``numpy.ndarray`` image (as produced by OpenCV).
        detections: Detection records with ``bbox``, ``label`` and ``track_id``.
        violations: Violation events to highlight in red.

    Returns:
        The annotated frame (a copy; the input is left untouched).

    Raises:
        NotImplementedError: Always, until Phase 5 implements the overlay.
    """
    raise NotImplementedError("Frame annotation is implemented in Phase 5")
