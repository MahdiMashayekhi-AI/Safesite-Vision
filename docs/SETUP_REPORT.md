# SafeSite Vision setup report

Last updated: **2026-11-27** (Asia/Tehran).

Repository: [MahdiMashayekhi-AI/Safesite-Vision](https://github.com/MahdiMashayekhi-AI/Safesite-Vision).
This is the current setup record, including the completion of the interrupted
bootstrap and the maintainer's revised ownership and Python requirements.

## Supported environment

- Python **3.12 only**: `requires-python = ">=3.12,<3.13"`, `.python-version` 3.12,
  CI 3.12, Docker `python:3.12-slim`.
- Package manager: uv; all dependency groups and `uv.lock` are committed.
- The maintainer explicitly chose 3.12 instead of the original 3.11 requirement.
- Local Torch 2.15.0+cpu and TorchVision 0.29.2+cpu were already working and were
  retained. No large Torch download or replacement with older local CUDA wheels
  was needed. Linux uses the explicit official CPU index in the lockfile.
- Docker is verified by GitHub Actions; it is not installed on this workstation.

## Delivered work

| Issue | PR | Branch | Result |
| --- | --- | --- | --- |
| #1 | #2 | `chore/1-project-scaffold` | Scaffold, dependency groups, configs, stubs and Makefile; merged |
| #3 | #4 | `chore/2-code-quality` | Ruff, mypy, pre-commit and editor settings; merged |
| #5 | #6 | `ci/3-github-actions-ci` | CI and PR-title checks; merged |
| #7 | #8 | `ci/4-cd-and-release` | Release, Docker and Dependabot workflows; merged |
| #9 | #11 | `docs/5-community-and-contributing` | Community files, Apache-2.0, templates and labels; merged |
| #45 | #46 | `docs/45-setup-report` | Initial setup report and protection script; merged as `3427a23` |
| #48 | #49 | `fix/48-protection-verify-fields` | Closed as superseded; the fix and regression tests shipped in #55 |
| #52, #48 | #55 | `fix/52-owner-review-policy` | Owner review policy and safe protection verification; merged as `a01312d` |
| #53 | #56 | `chore/53-development-quality` | Security/push hooks, Python 3.12, CPU builds and data ignores; merged as `2c99fe0` |
| #54 | #59 | `chore/54-dvc-backup` | DVC tracking, external backup, roadmap board and final documentation |

PRs #50 and #51 were closed after their compatible updates were incorporated into
#56 (setup-uv 10.4.0, Pydantic 2.14.4, Ruff 0.17.6 and FastAPI 0.165.0).
The Python 3.15 Docker bump in #10 was closed intentionally: only 3.12 is supported.
Dependabot now leaves Python minor/major image upgrades to deliberate review.
Subsequent patch PRs #57 (PR-title action 6.1.3) and #58 (PyYAML 6.0.4 and
Ultralytics 8.4.217) were reviewed and merged after green checks. The completion
branch includes both updates.

## Ownership and main protection

The owner is `@MahdiMashayekhi-AI`, the sole repository administrator and the sole
CODEOWNER for every path. `@Mohii722` has **write**, not admin, access.

Two enforcement layers implement the requested policy:

| Layer | Enforced behavior | Bypass |
| --- | --- | --- |
| Classic protection on `main` | PR required, green `ci-success` and `pr-title`, up-to-date branch, resolved conversations, linear history, no force push/deletion | None, including admins |
| Active owner-review ruleset | One code-owner approval for collaborator PRs; stale approvals dismissed | Repository admin, through a PR only |

The owner can merge their own PR without another review. This is a review-layer
bypass, not self-approval and not permission to push directly to `main`. The
successful owner merges of #55 and #56 exercised this path with green CI.
Collaborators cannot use it and need the owner's review. Do not promote a
collaborator to admin unless the policy is intentionally being changed.

Only Squash merge is enabled. Automatic head-branch deletion is enabled. Actions
has read-only default permissions and cannot approve PRs.

The reproducible script installs the review layer before changing the classic
review count. A failed ruleset request cannot silently remove review enforcement.
Read-only verification checks 22 live settings:

```powershell
uv run python scripts/setup_repo_protection.py --verify-only
```

To apply the declared settings deliberately as the owner:

```powershell
uv run python scripts/setup_repo_protection.py --dry-run
uv run python scripts/setup_repo_protection.py
```

An owner-authenticated direct-push probe was rejected with `GH013` and
"Changes must be made through a pull request." The remote main SHA was unchanged.
The probe used an empty tree change on a dangling commit, without committing on
the local main branch or disabling any hook.

## Local hooks and CI

Install all three hook stages in each clone:

```powershell
uv sync --all-groups
uv run pre-commit install --install-hooks
```

- Commit: `ruff-check`/format v0.17.6, whitespace/YAML/TOML checks, private-key
  detection, large-file guard, LF normalization, `no-commit-to-branch` for main
  and master, and Gitleaks staged-content scanning.
- Commit message: Conventional Commits.
- Push: Gitleaks committed-history scanning, mypy and pytest.
- Gitleaks 8.30.1 uses official prebuilt releases, verified against SHA-256
  manifests before extraction. It is cached under `~/.cache/safesite/gitleaks`.
  No local Go or Docker installation is needed. Findings are redacted.
- CI includes lint, typecheck, Python 3.12 tests, a full-history security scan,
  and the aggregate `ci-success`; PR-title validation runs separately.
- CI and the Docker build assert that Linux PyTorch has `torch.version.cuda is None`.
- Release tags build distributions and create GitHub Releases; Docker tags push to
  GHCR. No release tag was created as part of this setup completion.

## DVC dataset backup

The existing SH17 snapshot is represented by six DVC outputs: images, labels,
meta-data, voc_labels, train_files.txt and val_files.txt. The four directories each
contain 8,099 files: **32,398 files**, **14,237,350,242 bytes** in total.

Git contains the six small `.dvc` pointers, DVC configuration, and ignore rules.
Dataset bytes and `.dvc/cache` remain outside Git. `.gitignore` covers all data
subdirectories while allowing pointers, `.gitkeep` and DVC-generated ignore rules.

The local default remote is `external-backup` at **`E:/Datasets/SH17`**. The drive
path is stored only in `.dvc/config.local`, so it does not constrain collaborators.
The local cache uses copies. Existing loose files and `archive.zip` on that drive
are preserved; DVC objects live in its separate `files/md5` tree.

The DVC push completed and cloud status reports the cache and external remote
in sync. All **32,402 objects** (32,398 file objects plus four directory manifests)
passed independent MD5 verification, covering **14,237,350,242 dataset bytes**.
The read-only audit resumed after 10,000 logged successful checks against the
same six pointer hashes; every remaining object was verified. The reusable
verifier reads in creation order to reduce random HDD seeks.

```powershell
uv run dvc status
uv run dvc status --cloud -r external-backup
uv run python scripts/verify_dvc_backup.py --remote E:/Datasets/SH17
```

The integrity verifier is read-only and checks directory manifests plus every
referenced object's bytes. Tests cover corrupted/missing objects, unsafe hash
paths and an empty snapshot. See [backup and recovery](data_versioning.md).

## Roadmap board

[SafeSite Vision Roadmap](https://github.com/users/MahdiMashayekhi-AI/projects/2)
is linked to this repository. It uses Board layout grouped by Status:
**Backlog / In Progress / In Review / Done**.

All **33** Phase 1-6 tasks (#12-#44) are present, along with Foundation tasks.
The board has **43 issues** at setup completion. Seven milestones (Phase 0-6)
and issue labels are present. Completed Foundation issues are marked Done;
unfinished model/data/compliance work remains Backlog, not falsely closed.
The project retains private visibility. `@Mohii722` has WRITER access to the
board, while repository access remains write and never admin.

## Validation record

| Check | Result |
| --- | --- |
| `uv sync --all-groups --locked` | Passed on Python 3.12 |
| `make lint`, `make typecheck`, `make test` | Passed with 19 tests in the completed DVC environment |
| Commit and pre-push hooks | Passed, including staged and history Gitleaks scans |
| #55 CI | Passed; owner-policy PR merged |
| #56 CI and Docker build | Passed, including the Linux CPU assertion and security scan |
| Protection `--verify-only` | All 22 checks passed |
| Roadmap issue coverage | All #12-#44 present, no missing task |
| DVC workspace/cloud status and backup integrity | Backup synchronized; all 32,402 objects passed checksum validation |
| Final completion CI/Docker | [PR #59 checks](https://github.com/MahdiMashayekhi-AI/Safesite-Vision/pull/59/checks) are required before merge |

## Remaining product work, outside bootstrap

Phase 1-6 tasks remain open because their implementation has not been completed:
data provenance/licence review, reproducible download/conversion/deduplication,
training, tracking, association, compliance rules, serving and hardening.
The raw dataset's local backup does not complete those tasks or license it for
redistribution. Creating a release/GHCR publication is future release work.

The three personal files `Deep_learning_for_site_safety_Real_time.pdf`, `REPORTS.md`
and `UPDATES.md` were left untracked and were not added to `.gitignore`.
The temporary `docs/REMAINING_SETUP_AUDIT.md` was deleted as requested and was
never committed or added to `.gitignore`.
