"""Evaluate a trained detector on the validation/test split.

Reports mAP50, mAP50-95, per-class metrics and the confusion matrix, and appends
the numbers to ``docs/model_card.md``.

Usage:
    uv run python scripts/evaluate.py --weights models/ppe_yolo.pt --split test
"""

from __future__ import annotations

import typer

app = typer.Typer(add_completion=False, no_args_is_help=True)


@app.command()
def main(
    weights: str = typer.Option(..., "--weights", "-w", help="Path to the model checkpoint."),
    data: str = typer.Option("configs/data.yaml", help="Dataset definition."),
    split: str = typer.Option("val", help="Split to evaluate: val or test."),
    imgsz: int = typer.Option(640, help="Inference image size."),
) -> None:
    """Evaluate ``weights`` on ``split`` of ``data``."""
    del data, split, imgsz
    raise NotImplementedError(f"evaluate is not implemented yet (weights: {weights!r})")


if __name__ == "__main__":  # pragma: no cover - manual invocation only
    app()
