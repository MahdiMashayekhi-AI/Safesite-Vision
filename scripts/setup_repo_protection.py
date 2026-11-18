"""Apply repository settings and ``main`` branch protection.

Some of the configuration a healthy repository needs cannot live in a file that
GitHub reads: merge behaviour, Actions permissions and the branch protection rule
on ``main``. This script applies them through the GitHub API so the setup is
reproducible and reviewable instead of click-ops.

Usage:
    uv run python scripts/setup_repo_protection.py --dry-run
    uv run python scripts/setup_repo_protection.py
    uv run python scripts/setup_repo_protection.py --repo owner/name

Requires the GitHub CLI (``gh``) authenticated as a repository administrator.
A token with the ``repo`` scope is enough for a repository you own; organisation
repositories may additionally require an SSO-authorised token.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from typing import Any

BRANCH = "main"

# Only squash merges: one Conventional Commit per PR on `main`, no merge bubbles.
REPO_SETTINGS: dict[str, Any] = {
    "allow_squash_merge": True,
    "allow_merge_commit": False,
    "allow_rebase_merge": False,
    "delete_branch_on_merge": True,
    "allow_auto_merge": False,
    "squash_merge_commit_title": "PR_TITLE",
    "squash_merge_commit_message": "PR_BODY",
}

# Least privilege for workflows: read the repository, never approve reviews.
ACTION_PERMISSIONS: dict[str, Any] = {
    "default_workflow_permissions": "read",
    "can_approve_pull_request_reviews": False,
}

# The `main` protection rule. `enforce_admins: true` is the "do not allow
# bypassing" requirement: even administrators must open a reviewed PR.
BRANCH_PROTECTION: dict[str, Any] = {
    "required_status_checks": {
        "strict": True,
        "contexts": ["ci-success", "pr-title"],
    },
    "enforce_admins": True,
    "required_pull_request_reviews": {
        "dismiss_stale_reviews": True,
        "require_code_owner_reviews": True,
        "required_approving_review_count": 1,
        "require_last_push_approval": False,
    },
    "restrictions": None,
    "required_linear_history": True,
    "allow_force_pushes": False,
    "allow_deletions": False,
    "required_conversation_resolution": True,
    "lock_branch": False,
    "allow_fork_syncing": False,
}


def run_gh(args: list[str], stdin: str | None = None) -> str:
    """Run a ``gh`` command and return its stdout.

    Args:
        args: Arguments passed to ``gh``.
        stdin: Optional payload written to the process stdin.

    Returns:
        The stripped standard output.

    Raises:
        SystemExit: If ``gh`` exits non-zero, with the server message.
    """
    result = subprocess.run(
        ["gh", *args],
        input=stdin,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip()
        raise SystemExit(
            f"gh {' '.join(args)} failed:\n{message}\n\n"
            "Hints: the token needs admin rights on the repository (scope 'repo' for a "
            "repository you own). Verify with `gh auth status` and "
            "`gh repo view --json viewerPermission`."
        )
    return result.stdout.strip()


def api(
    method: str,
    path: str,
    payload: dict[str, Any] | None = None,
    *,
    dry_run: bool = False,
) -> Any:
    """Call the GitHub REST API through ``gh api``.

    Args:
        method: HTTP method, e.g. ``GET``, ``PATCH`` or ``PUT``.
        path: API path relative to ``/repos``, e.g. ``branches/main/protection``.
        payload: Optional JSON body.
        dry_run: When True, print the call instead of performing it.

    Returns:
        The parsed JSON response, or ``None`` in dry-run mode.
    """
    if dry_run:
        print(f"[dry-run] {method} {path}")
        if payload is not None:
            print(json.dumps(payload, indent=2))
        return None

    body = json.dumps(payload) if payload is not None else None
    raw = run_gh(["api", "--method", method, path, "--input", "-"], stdin=body)
    return json.loads(raw) if raw else None


def apply_repo_settings(repo: str, *, dry_run: bool) -> None:
    """Configure merge behaviour (squash only, delete head branches)."""
    api("PATCH", f"repos/{repo}", payload=REPO_SETTINGS, dry_run=dry_run)


def apply_action_permissions(repo: str, *, dry_run: bool) -> None:
    """Set the default workflow token permissions to read-only."""
    api(
        "PUT",
        f"repos/{repo}/actions/permissions/workflow",
        payload=ACTION_PERMISSIONS,
        dry_run=dry_run,
    )


def apply_branch_protection(repo: str, *, dry_run: bool) -> None:
    """Create or replace the branch protection rule for ``main``."""
    api(
        "PUT",
        f"repos/{repo}/branches/{BRANCH}/protection",
        payload=BRANCH_PROTECTION,
        dry_run=dry_run,
    )


def _enabled(field: Any) -> bool:
    """Read a protection flag that the API may return as an object or a bool.

    ``GET .../protection`` returns some flags as ``{"enabled": true}`` objects and
    others as bare booleans, so both shapes must be handled.

    Args:
        field: Either ``{"enabled": bool}``, a bare boolean or ``None``.

    Returns:
        True only when the flag is explicitly enabled.
    """
    if isinstance(field, dict):
        return field.get("enabled") is True
    return field is True


def verify(repo: str) -> int:
    """Print the effective configuration and its conformance checklist.

    Args:
        repo: Repository in ``owner/name`` form.

    Returns:
        0 when every required setting is in place, 1 otherwise.
    """
    settings = json.loads(
        run_gh(
            [
                "api",
                f"repos/{repo}",
                "--jq",
                "{allow_squash_merge,allow_merge_commit,allow_rebase_merge,delete_branch_on_merge}",
            ]
        )
    )
    workflow = json.loads(run_gh(["api", f"repos/{repo}/actions/permissions/workflow"]))
    protection = json.loads(run_gh(["api", f"repos/{repo}/branches/{BRANCH}/protection"]))

    reviews = protection.get("required_pull_request_reviews") or {}
    status_checks = protection.get("required_status_checks") or {}
    contexts = status_checks.get("contexts") or [
        check.get("context") for check in status_checks.get("checks", [])
    ]

    checks: list[tuple[str, bool]] = [
        ("squash merge enabled", settings.get("allow_squash_merge") is True),
        ("merge commits disabled", settings.get("allow_merge_commit") is False),
        ("rebase merge disabled", settings.get("allow_rebase_merge") is False),
        ("head branches deleted on merge", settings.get("delete_branch_on_merge") is True),
        ("workflow token is read-only", workflow.get("default_workflow_permissions") == "read"),
        ("PR required before merging", "required_pull_request_reviews" in protection),
        ("at least 1 approving review", reviews.get("required_approving_review_count", 0) >= 1),
        ("stale approvals dismissed", reviews.get("dismiss_stale_reviews") is True),
        ("code-owner review required", reviews.get("require_code_owner_reviews") is True),
        ("ci-success required", "ci-success" in contexts),
        ("pr-title required", "pr-title" in contexts),
        ("branches must be up to date", status_checks.get("strict") is True),
        (
            "conversation resolution required",
            _enabled(protection.get("required_conversation_resolution")),
        ),
        ("linear history required", _enabled(protection.get("required_linear_history"))),
        ("force pushes blocked", not _enabled(protection.get("allow_force_pushes"))),
        ("deletions blocked", not _enabled(protection.get("allow_deletions"))),
        ("admins cannot bypass", _enabled(protection.get("enforce_admins"))),
    ]

    width = max(len(name) for name, _ in checks)
    print(f"\nVerification for {repo}:{BRANCH}\n")
    for name, ok in checks:
        print(f"  [{'ok' if ok else 'MISSING'}] {name.ljust(width)}")

    failed = [name for name, ok in checks if not ok]
    if failed:
        print(f"\n{len(failed)} check(s) not satisfied: {', '.join(failed)}")
        return 1
    print("\nAll protection settings are in place.")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Entry point.

    Args:
        argv: Optional argument list (defaults to ``sys.argv[1:]``).

    Returns:
        Process exit code.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", help="Repository as owner/name (defaults to the current one).")
    parser.add_argument("--dry-run", action="store_true", help="Print the API calls only.")
    parser.add_argument("--skip-verify", action="store_true", help="Do not verify afterwards.")
    args = parser.parse_args(argv)

    repo = args.repo
    if not repo:
        repo = run_gh(["repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"])

    print(f"Applying repository configuration to {repo} (branch: {BRANCH})")
    apply_repo_settings(repo, dry_run=args.dry_run)
    apply_action_permissions(repo, dry_run=args.dry_run)
    apply_branch_protection(repo, dry_run=args.dry_run)

    if args.dry_run or args.skip_verify:
        print("\nDone (verification skipped).")
        return 0

    return verify(repo)


if __name__ == "__main__":  # pragma: no cover - manual invocation only
    sys.exit(main())
