"""Download the raw PPE datasets into ``data/raw/``.

Responsibilities (Phase 1 of the roadmap):

- Fetch every dataset registered in ``docs/datasets.md`` that permits use.
- Verify checksums and expected class coverage after download.
- Never write outside ``data/raw/`` and never commit the result.

Usage:
    uv run python scripts/download_data.py --dataset roboflow-ppe
"""

from __future__ import annotations

import typer

app = typer.Typer(add_completion=False, no_args_is_help=True)


@app.command()
def main(
    dataset: str = typer.Option(
        ..., "--dataset", "-d", help="Registered dataset key to download."
    ),
    output_dir: str = typer.Option("data/raw", help="Destination directory."),
    force: bool = typer.Option(
        False, "--force", help="Re-download even if the data exists."
    ),
) -> None:
    """Download ``dataset`` into ``output_dir``."""
    del output_dir, force
    raise NotImplementedError(
        f"download_data is not implemented yet (requested: {dataset!r})"
    )


if __name__ == "__main__":  # pragma: no cover - manual invocation only
    app()
