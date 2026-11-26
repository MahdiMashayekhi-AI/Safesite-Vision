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

# Non-bypassable baseline: EVERYONE needs a PR and green CI.
# Review requirements live in a separate ruleset with PR-only admin bypass.
BRANCH_PROTECTION: dict[str, Any] = {
    "required_status_checks": {
        "strict": True,
        "contexts": ["ci-success", "pr-title"],
    },
    "enforce_admins": True,
    "required_pull_request_reviews": {
        "dismiss_stale_reviews": True,
        "require_code_owner_reviews": False,
        "required_approving_review_count": 0,
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


REVIEW_RULESET: dict[str, Any] = {
    "name": "Owner review for collaborator pull requests",
    "target": "branch",
    "enforcement": "active",
    "conditions": {"ref_name": {"include": ["refs/heads/main"], "exclude": []}},
    # GitHub's built-in administrator role; collaborators retain write access.
    "bypass_actors": [
        {"actor_id": 5, "actor_type": "RepositoryRole", "bypass_mode": "pull_request"}
    ],
    "rules": [
        {
            "type": "pull_request",
            "parameters": {
                "required_approving_review_count": 1,
                "dismiss_stale_reviews_on_push": True,
                "require_code_owner_review": True,
                "require_last_push_approval": False,
                "required_review_thread_resolution": True,
                "allowed_merge_methods": ["squash"],
            },
        }
    ],
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


def apply_review_ruleset(repo: str, *, dry_run: bool) -> None:
    """Install review enforcement before relaxing classic review requirements."""
    existing = json.loads(run_gh(["api", f"repos/{repo}/rulesets", "--paginate"]))
    matches = [item for item in existing if item["name"] == REVIEW_RULESET["name"]]
    if len(matches) > 1:
        raise SystemExit(
            "Duplicate review rulesets found; reconcile them before applying settings."
        )
    path = f"repos/{repo}/rulesets"
    if matches:
        api("PUT", f"{path}/{matches[0]['id']}", REVIEW_RULESET, dry_run=dry_run)
    else:
        api("POST", path, REVIEW_RULESET, dry_run=dry_run)


def _enabled(field: Any) -> bool:
    """Read nested flags without treating enabled=false objects as true."""
    return field.get("enabled") is True if isinstance(field, dict) else field is True


def _review_matches(rules: list[dict[str, Any]]) -> bool:
    """Check required review fields while accepting additive GitHub API fields."""
    if len(rules) != 1 or rules[0].get("type") != "pull_request":
        return False
    actual = rules[0].get("parameters", {})
    expected = REVIEW_RULESET["rules"][0]["parameters"]
    return all(actual.get(key) == value for key, value in expected.items())


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

    rulesets = json.loads(run_gh(["api", f"repos/{repo}/rulesets", "--paginate"]))
    matching = [rule for rule in rulesets if rule["name"] == REVIEW_RULESET["name"]]
    review_rule = (
        json.loads(run_gh(["api", f"repos/{repo}/rulesets/{matching[0]['id']}"]))
        if len(matching) == 1
        else {}
    )
    collaborators = json.loads(run_gh(["api", f"repos/{repo}/collaborators", "--paginate"]))
    admins = {user["login"] for user in collaborators if user["role_name"] == "admin"}

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
        (
            "owner not blocked by classic reviews",
            reviews.get("required_approving_review_count") == 0,
        ),
        ("stale approvals dismissed", reviews.get("dismiss_stale_reviews") is True),
        ("classic code-owner gate disabled", reviews.get("require_code_owner_reviews") is False),
        ("review ruleset active", review_rule.get("enforcement") == "active"),
        (
            "review ruleset targets main",
            review_rule.get("conditions") == REVIEW_RULESET["conditions"],
        ),
        ("collaborators need owner review", _review_matches(review_rule.get("rules", []))),
        (
            "admin review bypass is PR-only",
            review_rule.get("bypass_actors") == REVIEW_RULESET["bypass_actors"],
        ),
        ("owner is the only administrator", admins == {repo.split("/")[0]}),
        ("ci-success required", "ci-success" in contexts),
        ("pr-title required", "pr-title" in contexts),
        ("branches must be up to date", status_checks.get("strict") is True),
        (
            "conversation resolution required",
            _enabled(protection.get("required_conversation_resolution")),
        ),
        ("linear history required", _enabled(protection.get("required_linear_history"))),
        (
            "force pushes blocked",
            (protection.get("allow_force_pushes") or {}).get("enabled") is False,
        ),
        ("deletions blocked", (protection.get("allow_deletions") or {}).get("enabled") is False),
        (
            "admins cannot bypass PR and CI",
            (protection.get("enforce_admins") or {}).get("enabled") is True,
        ),
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
    parser.add_argument("--verify-only", action="store_true", help="Read settings without writes.")
    args = parser.parse_args(argv)

    repo = args.repo
    if not repo:
        repo = run_gh(["repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"])

    if args.verify_only:
        return verify(repo)

    print(f"Applying repository configuration to {repo} (branch: {BRANCH})")
    apply_repo_settings(repo, dry_run=args.dry_run)
    apply_action_permissions(repo, dry_run=args.dry_run)
    apply_review_ruleset(repo, dry_run=args.dry_run)
    apply_branch_protection(repo, dry_run=args.dry_run)

    if args.dry_run or args.skip_verify:
        print("\nDone (verification skipped).")
        return 0

    return verify(repo)


if __name__ == "__main__":  # pragma: no cover - manual invocation only
    sys.exit(main())
