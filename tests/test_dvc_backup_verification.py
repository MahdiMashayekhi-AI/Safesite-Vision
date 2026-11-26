"""Backup verification must detect missing and corrupted content."""

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest
import yaml

SPEC = importlib.util.spec_from_file_location(
    "backup_verification", Path(__file__).parents[1] / "scripts" / "verify_dvc_backup.py"
)
assert SPEC is not None and SPEC.loader is not None
backup = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(backup)


def test_verified_directory_and_corruption_detection(tmp_path: Path) -> None:
    content = b"dataset fixture"
    digest = hashlib.md5(content).hexdigest()
    target = backup.object_path(tmp_path, digest)
    target.parent.mkdir(parents=True)
    target.write_bytes(content)
    manifest = json.dumps([{"md5": digest, "relpath": "example.txt"}]).encode()
    directory = hashlib.md5(manifest).hexdigest() + ".dir"
    manifest_path = backup.object_path(tmp_path, directory)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_bytes(manifest)
    pointer = tmp_path / "dataset.dvc"
    pointer.write_text(
        yaml.safe_dump({"outs": [{"hash": "md5", "md5": directory, "size": len(content)}]})
    )
    assert backup.verify(tmp_path, [pointer]) == (2, len(content))
    target.write_bytes(b"corrupt")
    with pytest.raises(ValueError, match="Corrupt"):
        backup.verify(tmp_path, [pointer])
    target.unlink()
    with pytest.raises(FileNotFoundError):
        backup.verify(tmp_path, [pointer])


def test_reject_invalid_object_path(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Invalid"):
        backup.object_path(tmp_path, "../../outside")


def test_empty_snapshot_is_not_success(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="No DVC pointers"):
        backup.verify(tmp_path, [])
