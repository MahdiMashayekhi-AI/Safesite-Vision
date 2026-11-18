"""Deduplicate images and create leakage-free train/val/test splits.

Writes the final ``data/processed/ppe`` tree consumed by ``configs/data.yaml``:
``images/{train,val,test}`` plus ``labels/{train,val,test}``.

Usage:
    uv run python scripts/dedup_split.py --source data/interim/yolo --seed 42
"""

from __future__ import annotations

import typer

app = typer.Typer(add_completion=False, no_args_is_help=True)


@app.command()
def main(
    source: str = typer.Option("data/interim/yolo", help="YOLO-format input directory."),
    destination: str = typer.Option("data/processed/ppe", help="Processed output directory."),
    ratios: str = typer.Option("0.7,0.15,0.15", help="train,val,test ratios."),
    seed: int = typer.Option(42, help="Random seed for reproducible splits."),
) -> None:
    """Deduplicate ``source`` and split it into train/val/test under ``destination``."""
    del destination, ratios, seed
    raise NotImplementedError(f"dedup_split is not implemented yet (source: {source!r})")


if __name__ == "__main__":  # pragma: no cover - manual invocation only
    app()
