"""Create or update the GitHub labels declared in ``.github/labels.yml``.

The YAML file is the single source of truth; this script only applies it. It is
idempotent: ``gh label create --force`` updates an existing label in place.

Usage:
    uv run python scripts/setup_labels.py --dry-run
    uv run python scripts/setup_labels.py
    uv run python scripts/setup_labels.py --repo owner/name

Requires the GitHub CLI (``gh``) installed and authenticated.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

LABELS_PATH = Path(__file__).resolve().parents[1] / ".github" / "labels.yml"


def load_labels(path: Path = LABELS_PATH) -> list[dict[str, str]]:
    """Load and validate the label definitions from ``path``.

    Args:
        path: Path to the labels YAML file.

    Returns:
        A list of ``{"name", "color", "description"}`` dictionaries.

    Raises:
        ValueError: If the file is malformed or a label entry is incomplete.
    """
    raw: Any = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or "labels" not in raw:
        raise ValueError(f"{path} must contain a top-level 'labels' list")

    labels: list[dict[str, str]] = []
    for entry in raw["labels"]:
        if not isinstance(entry, dict):
            raise ValueError(f"invalid label entry: {entry!r}")
        missing = {"name", "color", "description"} - entry.keys()
        if missing:
            raise ValueError(f"label {entry.get('name')!r} is missing {sorted(missing)}")
        labels.append(
            {
                "name": str(entry["name"]),
                "color": str(entry["color"]).lstrip("#").upper(),
                "description": str(entry["description"]),
            }
        )
    return labels


def resolve_repo(explicit: str | None) -> str:
    """Return ``owner/name`` for the current repository.

    Args:
        explicit: A ``owner/name`` string to use instead of asking ``gh``.

    Returns:
        The repository in ``owner/name`` form.

    Raises:
        SystemExit: If ``gh`` cannot determine the repository.
    """
    if explicit:
        return explicit
    result = subprocess.run(
        ["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit(f"could not determine the repository: {result.stderr.strip()}")
    return result.stdout.strip()


def sync_label(repo: str, label: dict[str, str], *, dry_run: bool = False) -> bool:
    """Create or update one label.

    Args:
        repo: Target repository in ``owner/name`` form.
        label: The label definition.
        dry_run: When True, only print the command.

    Returns:
        True when the label was applied (or would be, in dry-run mode).
    """
    command = [
        "gh",
        "label",
        "create",
        label["name"],
        "--repo",
        repo,
        "--color",
        label["color"],
        "--description",
        label["description"],
        "--force",
    ]
    if dry_run:
        print(f"[dry-run] {' '.join(command)}")
        return True

    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        print(f"FAILED  {label['name']}: {result.stderr.strip()}", file=sys.stderr)
        return False
    print(f"ok      {label['name']}")
    return True


def main(argv: list[str] | None = None) -> int:
    """Entry point.

    Args:
        argv: Optional argument list (defaults to ``sys.argv[1:]``).

    Returns:
        Process exit code: 0 when every label was applied.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", help="Target repository as owner/name.")
    parser.add_argument("--file", default=str(LABELS_PATH), help="Labels YAML file.")
    parser.add_argument("--dry-run", action="store_true", help="Print commands only.")
    args = parser.parse_args(argv)

    labels = load_labels(Path(args.file))
    repo = resolve_repo(args.repo)
    print(f"Applying {len(labels)} labels to {repo}")

    failures = [
        label["name"] for label in labels if not sync_label(repo, label, dry_run=args.dry_run)
    ]
    if failures:
        print(f"\n{len(failures)} label(s) failed: {', '.join(failures)}", file=sys.stderr)
        return 1

    print(f"\nDone. {len(labels)} labels are up to date.")
    return 0


if __name__ == "__main__":  # pragma: no cover - manual invocation only
    raise SystemExit(main())
