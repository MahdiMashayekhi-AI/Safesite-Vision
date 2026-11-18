"""Command-line interface for SafeSite Vision.

Entry point registered as the ``safesite`` console script in ``pyproject.toml``.
Subcommands are thin wrappers so that the same logic can be reused from the API
and from ``scripts/``.
"""

from __future__ import annotations

import typer

from safesite import __version__

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="SafeSite Vision - PPE detection and safety-compliance toolkit.",
)


@app.command()
def version() -> None:
    """Print the installed SafeSite Vision version."""
    typer.echo(f"safesite {__version__}")


@app.command()
def pipeline(
    source: str = typer.Option(
        ..., "--source", "-s", help="Video file, image or camera index to process."
    ),
    rules: str = typer.Option(
        "configs/compliance_rules.yaml",
        "--rules",
        help="Path to the compliance rule configuration.",
    ),
) -> None:
    """Run the end-to-end PPE compliance pipeline over a source."""
    typer.echo(
        f"[stub] pipeline(source={source!r}, rules={rules!r}) is not implemented yet; "
        "see Phase 3 in the roadmap.",
        err=True,
    )
    raise typer.Exit(code=1)


if __name__ == "__main__":  # pragma: no cover - manual invocation only
    app()
