"""Run a pinned official Gitleaks binary without requiring Go or Docker.

The release archive is checked against the publisher's SHA-256 manifest before
extracting only the executable. Downloads are cached outside the repository.
Any download, checksum or scan failure fails the hook and CI.
"""

from __future__ import annotations

import hashlib
import io
import platform
import subprocess
import sys
import tarfile
import urllib.request
import zipfile
from pathlib import Path

VERSION = "8.30.1"
BASE_URL = f"https://github.com/gitleaks/gitleaks/releases/download/v{VERSION}"


def download(name: str) -> bytes:
    """Read an asset from the pinned official release with a bounded timeout."""
    request = urllib.request.Request(f"{BASE_URL}/{name}", headers={"User-Agent": "safesite"})
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read()


def verify_checksum(data: bytes, name: str, manifest: str) -> None:
    """Reject missing or mismatched checksums before extracting any executable."""
    entries = dict(line.split(maxsplit=1)[::-1] for line in manifest.splitlines() if line.strip())
    expected = entries.get(name) or entries.get(f"*{name}")
    if expected is None or hashlib.sha256(data).hexdigest() != expected.lower():
        raise ValueError(f"Gitleaks checksum verification failed for {name}")


def executable() -> Path:
    """Find or install the verified binary for this operating system."""
    system = platform.system().lower()
    arch = {"amd64": "x64", "x86_64": "x64", "aarch64": "arm64", "arm64": "arm64"}.get(
        platform.machine().lower()
    )
    if system not in {"windows", "linux", "darwin"} or arch is None:
        raise RuntimeError(f"Unsupported Gitleaks platform: {system}/{platform.machine()}")
    filename = "gitleaks.exe" if system == "windows" else "gitleaks"
    cache = Path.home() / ".cache" / "safesite" / "gitleaks" / VERSION / f"{system}-{arch}"
    binary = cache / filename
    if binary.is_file():
        return binary
    extension = "zip" if system == "windows" else "tar.gz"
    asset = f"gitleaks_{VERSION}_{system}_{arch}.{extension}"
    data = download(asset)
    manifest = download(f"gitleaks_{VERSION}_checksums.txt").decode("utf-8")
    verify_checksum(data, asset, manifest)
    if system == "windows":
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            content = archive.read(filename)
    else:
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
            member = archive.extractfile(filename)
            if member is None:
                raise ValueError("Gitleaks executable is missing from the release archive")
            content = member.read()
    cache.mkdir(parents=True, exist_ok=True)
    temporary = binary.with_suffix(".tmp")
    temporary.write_bytes(content)
    temporary.chmod(0o755)
    temporary.replace(binary)
    return binary


if __name__ == "__main__":
    sys.exit(subprocess.run([str(executable()), *sys.argv[1:]], check=False).returncode)
