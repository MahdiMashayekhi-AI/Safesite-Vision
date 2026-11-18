"""End-to-end PPE compliance pipeline.

Stages (see ``docs/architecture.md``):

1. Detection      - Ultralytics YOLO over each frame.
2. Tracking       - ByteTrack assigns stable ``track_id`` values to persons.
3. Association    - PPE boxes are attached to the person that wears them.
4. Compliance     - The rule engine evaluates per-person equipment state.
5. Smoothing      - Temporal smoothing suppresses one-frame flicker.
6. Events         - Confirmed violations are emitted as violation events.

This module currently exposes the orchestration skeleton only; the stages are
implemented incrementally in Phase 3 of the roadmap.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__all__ = ["CompliancePipeline", "PipelineConfig"]


@dataclass(slots=True)
class PipelineConfig:
    """Configuration for :class:`CompliancePipeline`.

    Attributes:
        model_path: Path to the YOLO weights used for detection.
        tracker_config: Path to the ByteTrack configuration file.
        rules_config: Path to the compliance rule configuration file.
        confidence_threshold: Minimum detection confidence kept by the detector.
        device: Inference device understood by Ultralytics (``cpu``, ``0``, ...).
    """

    model_path: str = "models/ppe_yolo.pt"
    tracker_config: str = "configs/tracker.yaml"
    rules_config: str = "configs/compliance_rules.yaml"
    confidence_threshold: float = 0.25
    device: str = "cpu"
    metadata: dict[str, Any] = field(default_factory=dict)


class CompliancePipeline:
    """Orchestrate detection, tracking, association, rules and smoothing."""

    def __init__(self, config: PipelineConfig | None = None) -> None:
        """Create a pipeline, falling back to :class:`PipelineConfig` defaults."""
        self.config = config or PipelineConfig()

    def run(self, source: Any) -> list[Any]:
        """Process ``source`` and return the confirmed violation events.

        Args:
            source: A video path, an image path, a camera index or an iterable
                of frames, depending on the stage implementation.

        Raises:
            NotImplementedError: Always, until Phase 3 wires the stages together.
        """
        raise NotImplementedError("Pipeline wiring is implemented in Phase 3")
