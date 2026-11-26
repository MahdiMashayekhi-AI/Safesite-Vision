"""Regression checks for safe policy migration and GitHub response parsing."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from unittest.mock import patch

import pytest

SPEC = importlib.util.spec_from_file_location(
    "repo_protection", Path(__file__).parents[1] / "scripts" / "setup_repo_protection.py"
)
assert SPEC is not None and SPEC.loader is not None
protection = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(protection)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (True, True),
        (False, False),
        ({"enabled": True}, True),
        ({"enabled": False}, False),
        ({}, False),
        (None, False),
    ],
)
def test_github_enabled_field(value: object, expected: bool) -> None:
    """A nonempty disabled object must never be mistaken for an enabled flag."""
    assert protection._enabled(value) is expected


def test_failed_review_install_does_not_relax_classic_protection() -> None:
    """A denied ruleset API request must leave the old review requirement intact."""
    with (
        patch.object(protection, "apply_repo_settings"),
        patch.object(protection, "apply_action_permissions"),
        patch.object(protection, "apply_review_ruleset", side_effect=SystemExit("denied")),
        patch.object(protection, "apply_branch_protection") as baseline,
    ):
        with pytest.raises(SystemExit, match="denied"):
            protection.main(["--repo", "owner/repo"])
        baseline.assert_not_called()


def test_verify_only_cannot_write_settings() -> None:
    """Auditing settings must not reconfigure repository access."""
    with (
        patch.object(protection, "verify", return_value=0) as verify,
        patch.object(protection, "apply_repo_settings") as settings,
        patch.object(protection, "apply_review_ruleset") as review,
        patch.object(protection, "apply_branch_protection") as baseline,
    ):
        assert protection.main(["--repo", "owner/repo", "--verify-only"]) == 0
        verify.assert_called_once_with("owner/repo")
        settings.assert_not_called()
        review.assert_not_called()
        baseline.assert_not_called()
