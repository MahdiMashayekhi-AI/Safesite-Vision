# Contributing to SafeSite Vision

Thanks for taking the time to contribute. This document is the contract for how work
flows through this repository; following it keeps reviews fast and history readable.

- [Code of conduct](#code-of-conduct)
- [Getting set up](#getting-set-up)
- [Workflow](#workflow)
- [Branch naming](#branch-naming)
- [Commit messages](#commit-messages)
- [Code style](#code-style)
- [Testing](#testing)
- [Review rules](#review-rules)
- [Data and model rules](#data-and-model-rules)
- [Releases](#releases)
- [Reporting bugs and requesting features](#reporting-bugs-and-requesting-features)

## Code of conduct

Participation is governed by [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md). Report unacceptable
behaviour to the maintainers privately.

## Getting set up

**Prerequisites:** [uv](https://docs.astral.sh/uv/), git, and the
[GitHub CLI](https://cli.github.com/) (`gh`) for the issue/PR workflow.

```bash
git clone https://github.com/MahdiMashayekhi-AI/Safesite-Vision.git
cd Safesite-Vision

uv sync --all-groups                          # creates a Python 3.12 .venv with every dependency group
uv run pre-commit install --install-hooks     # installs pre-commit + commit-msg + pre-push hooks
```

Verify the environment before writing code:

```bash
make lint        # ruff check + ruff format --check
make typecheck   # mypy (strict)
make test        # pytest with coverage
```

`make` is optional but useful; each target is a thin wrapper over `uv run ...`.

Optional extras:

```bash
uv sync --group app       # FastAPI + Streamlit
uv sync --group export    # ONNX + ONNX Runtime
```

## Workflow

Every change follows the same path. **Nothing is committed directly to `main`** — it is a
protected branch.

1. **Issue first.** Search existing issues, then open one using the proper template
   (`bug_report`, `feature_request`, `task`) and label it.
2. **Branch** from an up-to-date `main`:
   ```bash
   git checkout main && git pull
   git checkout -b feat/42-association-iou-thresholds
   ```
3. **Commit** in small, reviewable steps following [Conventional Commits](#commit-messages).
4. **Push** and open a pull request against `main`, filling in every section of
   `.github/pull_request_template.md` and ending the description with `Closes #<issue>`.
5. **CI must be green.** Required checks: `ci-success` (lint + typecheck + tests) and
   `pr-title`. A failing or pending check blocks merging.
6. **Review.** Collaborator PRs require approval from `@MahdiMashayekhi-AI`, the
   code owner for every path. The owner may merge their own PR using the review-only
   administrator bypass. Everyone still needs a PR, green CI and resolved conversations.
7. **Squash merge.** The merge commit becomes one Conventional Commit on `main`; the head
   branch is deleted automatically.
8. **Sync** locally: `git checkout main && git pull`.

Keep pull requests focused. If a change is larger than roughly 400 changed lines, split it
— smaller PRs get better reviews and are easier to revert.

## Branch naming

`type/<issue-number>-short-desc`, lower-case, hyphen-separated, using the same types as
Conventional Commits:

| Prefix | Use for | Example |
| ------ | ------- | ------- |
| `feat/` | new functionality | `feat/12-tracking-byte-track-store` |
| `fix/` | bug fixes | `fix/31-association-occlusion` |
| `docs/` | documentation only | `docs/20-model-card` |
| `ci/` | workflows, tooling, automation | `ci/7-release-workflow` |
| `chore/` | maintenance, deps, scaffold | `chore/1-project-scaffold` |
| `refactor/` | internal restructuring, no behaviour change | `refactor/18-rule-engine` |
| `test/` | test-only changes | `test/24-rule-evaluation` |

## Commit messages

[Conventional Commits](https://www.conventionalcommits.org/) are enforced by a
`commit-msg` hook; the PR title is validated the same way by the `pr-title` workflow.

Format: `type(scope): subject`

- **type** — one of `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`,
  `ci`, `chore`, `revert`
- **scope** (optional) — `data`, `detection`, `tracking`, `association`, `compliance`,
  `api`, `docs`, `ci`, `deps`
- **subject** — imperative, lower-case, no trailing period, at most ~72 characters

Examples:

```
feat(compliance): add per-zone rule evaluation
fix(tracking): keep track ids stable across occlusions
docs(model-card): record baseline mAP50 and FPS
ci(docker): push image to ghcr on release tags
chore(deps): bump ultralytics to 8.4.215
```

Body (optional, wrapped at 72 characters) explains *why*, not *what*. `BREAKING CHANGE:`
in the footer marks a breaking change.

## Code style

- **Formatting and linting:** `ruff` with `line-length = 100` and rules `E, F, I, B, UP, N`
  (configured in `pyproject.toml`). Run `make format` before committing; pre-commit will
  also fix what it can.
- **Typing:** all public functions and methods are fully annotated. `mypy` runs in strict
  mode over `src/`; use `# type: ignore[code]` only with a short justification comment.
- **Docstrings:** Google style for public modules, classes and functions. Explain units and
  coordinate conventions (pixels vs normalised) — most integration bugs come from those.
- **Imports:** absolute (`from safesite.compliance import ...`), sorted by ruff/isort.
- **Config over code:** thresholds, class mappings and rule parameters belong in `configs/`,
  validated with pydantic, not hard-coded.
- **No dead code:** delete it instead of commenting it out; git remembers.

## Local security and push gates

The pinned Ruff hook is `ruff-check`. Commit hooks also normalize line endings to
LF, reject commits on main/master, and run Gitleaks against staged changes.
Before each push, Gitleaks scans committed history and mypy plus pytest run in the
locked project environment. CI repeats the history scan, so installing local
hooks is not the only protection. Never skip a failing hook to publish a change.
Gitleaks findings are redacted; resolve the cause before retrying. The runner
downloads the pinned official release, validates its SHA-256 checksum, and caches
it under `~/.cache/safesite/gitleaks`; Go and Docker are not required locally.

## Testing

- Framework: `pytest`. Run the suite with `make test` (adds coverage) or
  `uv run pytest -q`.
- Name tests `test_<unit>_<behaviour>` and keep them deterministic — no network, no real
  video files; build small synthetic arrays instead.
- **Every bug fix needs a regression test** that fails before the fix and passes after.
- New logic in `src/safesite/` should come with unit tests; aim to keep overall coverage
  from dropping.
- Cover the edges: empty frame, all persons missing PPE, one person with a false positive
  on a single frame, two overlapping persons.

## Review rules

- **Collaborator PRs require the project owner's approval.** `CODEOWNERS` assigns every
  path to `@MahdiMashayekhi-AI`. Keep collaborators at the write role.
- **Owner PRs can be merged without another reviewer.** A separate review ruleset
  grants the sole administrator a pull-request-only review bypass. GitHub does not
  support self-approval; use the merge/bypass option instead.
- **Nobody can push directly to main**, including the owner. Classic protection
  enforces PRs, green CI, up-to-date branches and resolved conversations for everyone.
- Reviews check, in order: correctness, test coverage of the change, boundary handling,
  config/schema compatibility, naming and docs.
- A new commit **dismisses stale approvals** — re-request a review after pushing changes.
- Resolve every conversation before merging; do not self-resolve a reviewer's comment.
- Reviewers: respond with a clear block/approve decision, or `nit:` for non-blocking
  suggestions.
- Do not merge with failing or skipped required checks. Only the owner may bypass
  the separate review layer; the PR and CI baseline remains mandatory.

## Data and model rules

These are hard rules — a PR that breaks them is rejected.

- **Never commit** datasets, images, videos, model weights (`.pt`, `.pth`, `.onnx`,
  `.engine`), training runs or experiment databases. `.gitignore` and the pre-commit
  `check-added-large-files` hook (500 KB) enforce this; `uv.lock` is the only large file
  that is committed.
- Keep artefacts in `data/` and `models/`; both are ignored except for `.gitkeep`.
- Every dataset needs a row in [`docs/datasets.md`](docs/datasets.md) with its **licence**,
  version, class mapping and commercial-use status *before* it is used in a PR.
- Only use data whose licence permits the intended use. Do not add data with unclear
  licensing.
- Do not commit footage containing identifiable people without consent and a retention
  policy; anonymise samples used in docs.
- Record every trained checkpoint in [`docs/model_card.md`](docs/model_card.md) (version,
  metrics, data, limitations) and publish weights as release assets, not in git.
- Reproducibility: pin the seed, dataset version and `uv.lock` for any reported metric.

## Releases

Releases are cut from `main` by pushing a semver tag:

```bash
git checkout main && git pull
git tag -a v0.2.0 -m "v0.2.0"
git push origin v0.2.0
```

The `Release` workflow builds the distributions, verifies the tag matches
`project.version` in `pyproject.toml`, and publishes a GitHub Release with generated
changelog notes. The `Docker` workflow publishes the image to `ghcr.io`.

## Reporting bugs and requesting features

- Read [`docs/architecture.md`](docs/architecture.md) first — it explains the module
  boundaries and where a fix probably belongs.
- Use the issue templates; include reproduction steps, expected vs actual behaviour, and
  environment details (`uv --version`, OS, Python version).
- For security vulnerabilities follow [`SECURITY.md`](SECURITY.md) instead of opening an
  issue.
