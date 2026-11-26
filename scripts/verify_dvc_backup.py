"""Read and verify every object referenced by DVC pointers in a local backup.

Usage: uv run python scripts/verify_dvc_backup.py --remote E:/Datasets/SH17
This command never changes dataset files, DVC pointers, cache or backup objects.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import yaml


def object_path(remote: Path, digest: str) -> Path:
    """Resolve a DVC MD5 object without allowing paths outside its object store."""
    if re.fullmatch(r"[0-9a-f]{32}(?:\.dir)?", digest) is None:
        raise ValueError(f"Invalid DVC object hash: {digest!r}")
    return remote / "files" / "md5" / digest[:2] / digest[2:]


def check_object(remote: Path, digest: str) -> None:
    """Fail if a stored object is missing or differs from its recorded digest."""
    path = object_path(remote, digest)
    with path.open("rb") as stream:
        actual = hashlib.file_digest(stream, "md5").hexdigest()
    if actual != digest.removesuffix(".dir"):
        raise ValueError(f"Corrupt DVC backup object: {digest}")


def verify(remote: Path, pointers: list[Path]) -> tuple[int, int]:
    """Verify manifests before following their file references, then all objects."""
    if not pointers:
        raise ValueError("No DVC pointers found")
    objects: set[str] = set()
    total_bytes = 0
    for pointer in pointers:
        data = yaml.safe_load(pointer.read_text(encoding="utf-8"))
        for output in data["outs"]:
            if output.get("hash") != "md5":
                raise ValueError(f"Unsupported DVC hash in {pointer}")
            digest = output["md5"]
            objects.add(digest)
            total_bytes += output["size"]
            if digest.endswith(".dir"):
                check_object(remote, digest)
                manifest = json.loads(object_path(remote, digest).read_text(encoding="utf-8"))
                objects.update(item["md5"] for item in manifest)
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = pool.map(lambda digest: check_object(remote, digest), sorted(objects))
        for count, _ in enumerate(results, 1):
            if count % 5000 == 0:
                print(f"Verified {count}/{len(objects)} objects", flush=True)
    return len(objects), total_bytes


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--remote", required=True, type=Path)
    parser.add_argument("--pointers", type=Path, default=Path("data/raw"))
    args = parser.parse_args()
    count, size = verify(args.remote, sorted(args.pointers.glob("*.dvc")))
    print(f"Verified {count} objects; dataset size {size:,} bytes. No changes made.")
