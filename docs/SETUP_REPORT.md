# Setup Report — SafeSite Vision

Record of how the repository was bootstrapped: tooling, CI/CD, standards, roadmap and
repository settings. Written so either maintainer can reproduce or audit the setup.

- **Repository:** [MahdiMashayekhi-AI/Safesite-Vision](https://github.com/MahdiMashayekhi-AI/Safesite-Vision) (public)
- **Date:** 2026-11-18
- **Package manager:** uv · **Python:** 3.12 (`requires-python = ">=3.12"`) · **CI matrix:** 3.12 + 3.13
- **Bot policy:** every change landed through Issue → Branch → PR → CI → Squash merge

## 1. Environment at setup time

| Item | Value |
| ---- | ----- |
| `git remote -v` | `origin → https://github.com/MahdiMashayekhi-AI/Safesite-Vision.git` |
| Default branch | `main` (single `Initial commit` before this work) |
| `gh auth status` | `MahdiMashayekhi-AI`, scopes `gist, read:org, repo, workflow` (viewer permission: **ADMIN**) |
| `uv` | **was not installed** → installed `uv 0.13.9`; `uv.lock` committed |
| `python` | only 3.15 on PATH → uv pinned and provisioned **3.12** (`.python-version`) |
| `git user.name/email` | **not configured** → set repo-locally to `Mahdi Mashayekhi <108976550+MahdiMashayekhi-AI@users.noreply.github.com>` |
| `make` | **not installed** → GNU Make 3.81 installed via `winget` for local target verification |
| Docker | not installed on the workstation → the `Docker` workflow on CI is the validation path |

## 2. Delivered work (Issue → Branch → PR)

| Step | Issue | PR | Branch | Title | Merge commit |
| ---- | ----- | -- | ------ | ----- | ------------ |
| 1 | [#1](https://github.com/MahdiMashayekhi-AI/Safesite-Vision/issues/1) | [#2](https://github.com/MahdiMashayekhi-AI/Safesite-Vision/pull/2) | `chore/1-project-scaffold` | chore: scaffold uv project structure with src layout | `3f9d1af` |
| 2 | [#3](https://github.com/MahdiMashayekhi-AI/Safesite-Vision/issues/3) | [#4](https://github.com/MahdiMashayekhi-AI/Safesite-Vision/pull/4) | `chore/2-code-quality` | chore: configure ruff, mypy, pre-commit and editorconfig | `e5f4e54` |
| 3 | [#5](https://github.com/MahdiMashayekhi-AI/Safesite-Vision/issues/5) | [#6](https://github.com/MahdiMashayekhi-AI/Safesite-Vision/pull/6) | `ci/3-github-actions-ci` | ci: add GitHub Actions pipeline and PR title validation | `ce1d8ad` |
| 4 | [#7](https://github.com/MahdiMashayekhi-AI/Safesite-Vision/issues/7) | [#8](https://github.com/MahdiMashayekhi-AI/Safesite-Vision/pull/8) | `ci/4-cd-and-release` | ci: add release and docker delivery workflows | `ad00a19` |
| 5 | [#9](https://github.com/MahdiMashayekhi-AI/Safesite-Vision/issues/9) | [#11](https://github.com/MahdiMashayekhi-AI/Safesite-Vision/pull/11) | `docs/5-community-and-contributing` | docs: add community standards, licence and contribution guides | `5bcd7a6` |
| 6 | — (metadata only, by design) | — | — | chore: roadmap milestones and issues | — |
| 7 | [#45](https://github.com/MahdiMashayekhi-AI/Safesite-Vision/issues/45) | [#46](https://github.com/MahdiMashayekhi-AI/Safesite-Vision/pull/46) | `docs/45-setup-report` | docs: add setup report and reproducible branch protection | this PR |

Every PR was squash-merged after `ci-success`, `pr-title` and the Docker build (where
triggered) passed, and its head branch was deleted on merge.

### What each step delivered

1. **Scaffold** — `uv init --package` (`safesite`, src layout), core dependencies, `dev`/`app`/`export`
   groups, `uv.lock`, config samples (`data.yaml`, `train_baseline.yaml`, `tracker.yaml`,
   `compliance_rules.yaml`), module skeletons, script stubs, FastAPI + Streamlit stubs, smoke tests,
   ML-aware `.gitignore`, `.gitattributes`, `Makefile`, docs templates.
2. **Code quality** — ruff (line length 100; `E,F,I,B,UP,N`), strict mypy, pytest + coverage config,
   pre-commit (ruff, ruff-format, hygiene hooks, private-key detection, 500 KB large-file guard,
   Conventional Commits via `commit-msg`), `.editorconfig`.
3. **CI** — `ci.yml` (`lint`, `typecheck`, `test` matrix, aggregate `ci-success`), `pr-title.yml`
   (`amannn/action-semantic-pull-request`), least-privilege permissions, uv caching keyed on `uv.lock`.
4. **CD** — `release.yml` (tag → build → version guard → GitHub Release with generated notes),
   `docker.yml` (PR build only; tag → GHCR push), multi-stage non-root `Dockerfile`,
   `.dockerignore`, `dependabot.yml` (uv, actions, docker).
5. **Community** — professional README with badges/architecture/roadmap, CONTRIBUTING with the full
   workflow, Contributor Covenant 2.1, SECURITY policy, **Apache-2.0** licence, CODEOWNERS
   (`@MahdiMashayekhi-AI`, `@Mohii722`), PR template, three issue forms + `config.yml`
   (blank issues disabled), `labels.yml` + `scripts/setup_labels.py`, 14 labels applied.
6. **Roadmap** — 7 milestones (Phase 0–6) and 33 issues covering every task of Phases 1–6, each with
   labels and the matching milestone.
7. **This report** — plus `scripts/setup_repo_protection.py`, the reproducible source of truth for the
   repository settings and branch protection described below.

## 3. CI/CD behaviour

| Workflow | Trigger | Jobs | Permissions |
| -------- | ------- | ---- | ----------- |
| `ci.yml` | `pull_request`, `push` to `main` | `lint`, `typecheck`, `test (py3.12)`, `test (py3.13)`, **`ci-success`** | `contents: read` |
| `pr-title.yml` | `pull_request_target` (opened/edited/reopened/synchronize) | **`pr-title`** | `contents: read`, `pull-requests: read` |
| `release.yml` | tag `v*.*.*` | `build distributions` → `publish GitHub release` | `contents: read` → `contents: write` (release job only) |
| `docker.yml` | PR on Docker-related paths, tag `v*.*.*`, manual | `build image` (push only on tags) | `contents: read`, `packages: write` |

Observations from the runs on this setup:

- First CI run failed in 3 s: `astral-sh/setup-uv@v10` does not resolve — the action publishes patch
  tags but no moving `v10` alias. All actions are now pinned to **exact release tags**.
- The Docker build takes ~16–17 minutes (torch + ultralytics), so it is path-filtered.
- `pr-title` cannot validate the PR that introduces it (`pull_request_target` runs the workflow from
  the default branch); it has been green on every PR after #6.
- The Docker build on PR #11 caught a real defect: PEP 639 `license-files = ["LICENSE"]` needs
  `LICENSE` in the build context, which the `Dockerfile` did not copy. Fixed in `8e89981`.

## 4. Local acceptance criteria

| Command | Result |
| ------- | ------ |
| `uv sync --all-groups` | ✅ resolves 121 packages, lockfile committed |
| `make lint` | ✅ `ruff check` + `ruff format --check` clean |
| `make typecheck` | ✅ `mypy` strict, no issues |
| `make test` | ✅ 4 passed with coverage |
| `uv run pre-commit run --all-files` | ✅ all hooks pass |
| `uv build` | ✅ sdist + wheel (with `license = "Apache-2.0"`, `license-files`) |
| Non-conventional commit message | ✅ rejected by `conventional-pre-commit` |

## 5. Repository settings

Applied by `uv run python scripts/setup_repo_protection.py` (idempotent, `--dry-run` supported):

| Setting | Value |
| ------- | ----- |
| Allow merge commits | ❌ disabled |
| Allow rebase merging | ❌ disabled |
| Allow squash merging | ✅ enabled (`PR_TITLE` + `PR_BODY`) |
| Automatically delete head branches | ✅ enabled |
| Actions: default workflow permissions | `read` (read-only) |
| Actions: allow GitHub Actions to approve PR reviews | ❌ disabled |

## 6. Branch protection for `main`

| Rule | Value |
| ---- | ----- |
| Require a pull request before merging | ✅ |
| Required approving reviews | **1** |
| Dismiss stale approvals on new commits | ✅ |
| Require review from Code Owners | ✅ |
| Require status checks | `ci-success`, `pr-title` |
| Require branches to be up to date | ✅ (strict) |
| Require conversation resolution | ✅ |
| Require linear history | ✅ |
| Block force pushes | ✅ |
| Block deletions | ✅ |
| Do not allow bypassing (admins enforced) | ✅ `enforce_admins: true` |

### How it is applied and verified

```bash
# Preview the exact API payloads
uv run python scripts/setup_repo_protection.py --dry-run

# Apply, then verify with a built-in 17-point checklist
uv run python scripts/setup_repo_protection.py

# Independent confirmation
gh api repos/MahdiMashayekhi-AI/Safesite-Vision/branches/main/protection

# Direct pushes must now be rejected
git checkout main
git commit --allow-empty -m "chore: probe main protection"
git push origin main   # expected: remote rejected (protected branch)
git reset --hard origin/main
```

If `gh api` fails with 403/404, the token lacks admin rights on the repository. In that case the
equivalent UI path is **Settings → Branches → Add branch protection rule** (use the values in the
table above), **Settings → General → Merge button** (squash only, auto-delete head branches) and
**Settings → Actions → General → Workflow permissions → Read repository contents and packages
permissions**.

## 7. Labels, milestones and roadmap issues

**Labels** (`type:*`, `area:*`, `priority:*`, `good first issue`, `dependencies`) are declared in
`.github/labels.yml` and applied with `uv run python scripts/setup_labels.py`; they are also
back-filled onto issues #1, #3, #5, #7 and #9.

| Milestone | Issues |
| --------- | ------ |
| Phase 0 - Foundation | #1, #3, #5, #7, #9, #45 (setup work, delivered) |
| Phase 1 - Data pipeline | #12, #13, #14, #15, #16 |
| Phase 2 - Detection baseline | #17, #18, #19, #20, #21, #22 |
| Phase 3 - Tracking and association | #23, #24, #25, #26, #27 |
| Phase 4 - Compliance engine | #28, #29, #30, #31, #32, #33 |
| Phase 5 - Serving and demo | #34, #35, #36, #37, #38 |
| Phase 6 - Hardening and release | #39, #40, #41, #42, #43, #44 |

## 8. Decisions and deviations

1. **Python matrix is 3.12 + 3.13, not 3.11 + 3.12.** `requires-python = ">=3.12"` makes a 3.11 job
   impossible to install; 3.13 is the forward-compatibility guard instead.
2. **Actions are pinned to exact tags** (`checkout@v7.0.1`, `setup-uv@v10.3.3`,
   `action-semantic-pull-request@v6.1.2`, `upload-artifact@v7.0.2`, `download-artifact@v8.0.2`,
   `build-push-action@v7.4.0`, `setup-buildx-action@v4.4.1`, `login-action@v4.8.0`,
   `metadata-action@v6.2.0`, `action-gh-release@v3.0.4`) because moving major aliases are not
   consistently published.
3. **Apache-2.0 replaced MIT**, as agreed; the README carries an explicit note that Ultralytics YOLO
   is AGPL-3.0 and that the Apache licence covers this repository's code only.
4. **Branch protection is applied last**, immediately after this PR merges. Rationale: GitHub forbids
   self-approval and `@Mohii722` is not a collaborator yet, so enabling "1 approval + no bypass"
   earlier would have made the remaining PRs unmergeable for everyone, including admins.
5. **PR 6 has no branch/PR by design** — it only created milestones and issues, as specified.
6. **`make` targets were verified locally** with GNU Make 3.81 on Windows; CI runs the same underlying
   `uv run` commands, so `Makefile` drift is caught by review, not CI.
7. **uv was installed via `pip install uv`** on the workstation because it was missing; CI installs it
   with `astral-sh/setup-uv`.

## 9. Known gaps / follow-ups

| Item | Owner | Action |
| ---- | ----- | ------ |
| GitHub Projects board (Backlog / In Progress / In Review / Done) | maintainer | `gh auth refresh -s project,read:project`, then the board can be created and the 33 issues added |
| `@Mohii722` not yet a collaborator | maintainer | invite via **Settings → Collaborators** so CODEOWNERS can request reviews and the approval rule is satisfiable |
| Post-protection merge flow | both | from now on every PR needs one approval from the other maintainer |
| Dependabot | both | review the weekly grouped PRs (a `python:3.15-slim` image bump already appeared) |
| First release | both | push `v0.2.0` once Phase 1 lands, to exercise `release.yml` and the GHCR push |

## 10. Reproducing this setup

```bash
git clone https://github.com/MahdiMashayekhi-AI/Safesite-Vision.git
cd Safesite-Vision
uv sync --all-groups
uv run pre-commit install --install-hooks
make lint && make typecheck && make test

# Repository-level configuration (admin only)
uv run python scripts/setup_labels.py
uv run python scripts/setup_repo_protection.py
```
