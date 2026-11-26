"""The security bootstrap must fail closed on corrupt or unsigned downloads."""

import hashlib
import importlib.util
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location(
    "gitleaks_bootstrap", Path(__file__).parents[1] / "scripts" / "run_gitleaks.py"
)
assert SPEC is not None and SPEC.loader is not None
bootstrap = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bootstrap)


def test_valid_release_checksum() -> None:
    data = b"release archive"
    checksum = hashlib.sha256(data).hexdigest()
    bootstrap.verify_checksum(data, "release.zip", f"{checksum}  release.zip\n")


@pytest.mark.parametrize("manifest", ["", "0" * 64 + "  release.zip", "a" * 64 + "  other.zip"])
def test_missing_or_invalid_checksum_fails_closed(manifest: str) -> None:
    with pytest.raises(ValueError, match="checksum verification failed"):
        bootstrap.verify_checksum(b"archive", "release.zip", manifest)
