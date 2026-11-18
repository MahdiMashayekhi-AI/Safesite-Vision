"""Smoke tests: the package installs, imports and exposes its public surface."""

from __future__ import annotations

import safesite
from safesite import pipeline, visualization


def test_version_is_exposed() -> None:
    """The package must expose a non-empty ``__version__`` string."""
    assert isinstance(safesite.__version__, str)
    assert safesite.__version__


def test_pipeline_config_defaults() -> None:
    """``PipelineConfig`` must be constructible with sane defaults."""
    config = pipeline.PipelineConfig()
    assert config.confidence_threshold == 0.25
    assert config.model_path.endswith(".pt")
    assert config.device == "cpu"


def test_pipeline_accepts_explicit_config() -> None:
    """The pipeline must keep the exact config instance it is given."""
    config = pipeline.PipelineConfig(confidence_threshold=0.5, device="cuda:0")
    assert pipeline.CompliancePipeline(config).config is config


def test_visualization_surface() -> None:
    """The visualization module must expose the annotation entry point."""
    assert callable(visualization.annotate_frame)
