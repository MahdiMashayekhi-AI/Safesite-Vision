"""Convert raw annotations into Ultralytics YOLO format.

Maps every source label space onto the fixed class ids in ``configs/data.yaml``
and writes ``data/interim/yolo`` with one ``.txt`` label file per image.

Usage:
    uv run python scripts/convert_to_yolo.py --source data/raw --class-map configs/data.yaml
"""

from __future__ import annotations

import typer

app = typer.Typer(add_completion=False, no_args_is_help=True)


@app.command()
def main(
    source: str = typer.Option("data/raw", help="Raw dataset directory."),
    destination: str = typer.Option("data/interim/yolo", help="Output directory (YOLO layout)."),
    class_map: str = typer.Option("configs/data.yaml", help="Dataset/class definition file."),
) -> None:
    """Convert ``source`` annotations to YOLO format under ``destination``."""
    del destination, class_map
    raise NotImplementedError(f"convert_to_yolo is not implemented yet (source: {source!r})")


if __name__ == "__main__":  # pragma: no cover - manual invocation only
    app()
