"""Export a trained checkpoint to ONNX (and optionally TensorRT).

The exported graph is written to ``models/`` and is never committed: it exceeds
the repository size policy.

Usage:
    uv run python scripts/export_onnx.py --weights models/ppe_yolo.pt --half
"""

from __future__ import annotations

import typer

app = typer.Typer(add_completion=False, no_args_is_help=True)


@app.command()
def main(
    weights: str = typer.Option(
        ..., "--weights", "-w", help="Path to the model checkpoint."
    ),
    imgsz: int = typer.Option(640, help="Export image size."),
    half: bool = typer.Option(False, "--half", help="Export with float16 precision."),
    simplify: bool = typer.Option(True, help="Run ONNX graph simplification."),
) -> None:
    """Export ``weights`` to ONNX."""
    del imgsz, half, simplify
    raise NotImplementedError(
        f"export_onnx is not implemented yet (weights: {weights!r})"
    )


if __name__ == "__main__":  # pragma: no cover - manual invocation only
    app()
