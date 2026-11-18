"""Benchmark throughput and latency of the detector across backends.

Measures end-to-end FPS for PyTorch and ONNX Runtime on CPU, and writes a markdown
table to ``docs/`` so the numbers in the README stay reproducible.

Usage:
    uv run python scripts/benchmark_fps.py --weights models/ppe_yolo.pt --frames 300
"""

from __future__ import annotations

import typer

app = typer.Typer(add_completion=False, no_args_is_help=True)


@app.command()
def main(
    weights: str = typer.Option(..., "--weights", "-w", help="Path to the model checkpoint."),
    frames: int = typer.Option(300, min=1, help="Number of frames to time."),
    imgsz: int = typer.Option(640, help="Inference image size."),
    device: str = typer.Option("cpu", help="Inference device."),
) -> None:
    """Benchmark ``weights`` over ``frames`` synthetic/real frames."""
    del frames, imgsz, device
    raise NotImplementedError(f"benchmark_fps is not implemented yet (weights: {weights!r})")


if __name__ == "__main__":  # pragma: no cover - manual invocation only
    app()
