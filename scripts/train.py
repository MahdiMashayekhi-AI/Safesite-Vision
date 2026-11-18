"""Train a YOLO PPE detector with Ultralytics.

Wraps ``ultralytics.YOLO.train`` with the hyper-parameters from a config file and
writes artefacts to ``runs/train/<name>`` (ignored by git).

Usage:
    uv run python scripts/train.py --config configs/train_baseline.yaml
"""

from __future__ import annotations

import typer

app = typer.Typer(add_completion=False, no_args_is_help=True)


@app.command()
def main(
    config: str = typer.Option(
        "configs/train_baseline.yaml", "--config", "-c", help="Training config."
    ),
    resume: bool = typer.Option(False, help="Resume the last interrupted run."),
) -> None:
    """Train a detector using the hyper-parameters in ``config``."""
    del resume
    raise NotImplementedError(f"train is not implemented yet (config: {config!r})")


if __name__ == "__main__":  # pragma: no cover - manual invocation only
    app()
