# SafeSite Vision

**Real-time PPE detection and safety-compliance analytics for industrial sites.**

[![CI](https://github.com/MahdiMashayekhi-AI/Safesite-Vision/actions/workflows/ci.yml/badge.svg)](https://github.com/MahdiMashayekhi-AI/Safesite-Vision/actions/workflows/ci.yml)
[![Docker](https://github.com/MahdiMashayekhi-AI/Safesite-Vision/actions/workflows/docker.yml/badge.svg)](https://github.com/MahdiMashayekhi-AI/Safesite-Vision/actions/workflows/docker.yml)
[![Release](https://img.shields.io/github/v/release/MahdiMashayekhi-AI/Safesite-Vision?sort=semver)](https://github.com/MahdiMashayekhi-AI/Safesite-Vision/releases)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12%20%7C%203.13-blue.svg)](pyproject.toml)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

SafeSite Vision turns site video into actionable safety-compliance events. It detects
persons and personal protective equipment (PPE) with YOLO, keeps identity stable with
ByteTrack, associates each piece of equipment with the person wearing it, evaluates
configurable compliance rules, smooths noisy per-frame decisions over time, and emits
violation events that an API or dashboard can consume.

> **Status:** early development. The scaffold, tooling, CI/CD and standards are in place;
> model training and the compliance engine are tracked in the [roadmap](#roadmap).

## Why

Manual PPE inspection does not scale and is inconsistent. A camera-based system that
reports *who* is missing *which* equipment, *where*, and *for how long* lets safety teams
act on evidence instead of spot checks — while keeping a human in the loop for every
consequence.

## Features

- **PPE detection** — YOLO (Ultralytics) detector for persons, helmets, vests, gloves,
  boots and goggles, including explicit "missing equipment" classes.
- **Multi-object tracking** — ByteTrack keeps a stable `track_id` per person so a
  violation can be attributed over time rather than per frame.
- **PPE-to-person association** — geometric matching of equipment boxes to the person
  who wears them, robust to overlapping workers.
- **Compliance rule engine** — declarative YAML rules (per zone, per severity) validated
  with pydantic at load time.
- **Temporal smoothing** — a violation must persist for N frames before it is reported
  and is rate-limited by a cooldown, which removes single-frame flicker.
- **Violation events** — a single typed event schema consumed by the API, the demo and
  future alerting.
- **Serving** — FastAPI service plus a Streamlit demo, shipped as a non-root CPU
  container image.

## Architecture

```
 video / RTSP / image
          |
          v
  +----------------+     +----------------+     +------------------------+
  | YOLO detector  | --> |   ByteTrack    | --> | PPE-to-person          |
  | (Ultralytics)  |     |  (track_id)    |     | association            |
  +----------------+     +----------------+     +------------------------+
                                                          |
                                                          v
                                               +------------------------+
                                               | Compliance rule engine |
                                               | configs/compliance_    |
                                               | rules.yaml             |
                                               +------------------------+
                                                          |
                                                          v
                                               +------------------------+
                                               | Temporal smoothing     |
                                               | min consecutive frames |
                                               +------------------------+
                                                          |
                                                          v
                                               +------------------------+
                                               | Violation events       |
                                               +------------------------+
                                                    |              |
                                                    v              v
                                             FastAPI /events   Streamlit demo
```

More detail: [`docs/architecture.md`](docs/architecture.md).

## Quick start

Requirements: [uv](https://docs.astral.sh/uv/) (Python 3.12 is installed by uv if missing).

```bash
git clone https://github.com/MahdiMashayekhi-AI/Safesite-Vision.git
cd Safesite-Vision

# Install every dependency group and create .venv
uv sync --all-groups

# Install the git hooks (ruff, formatting, commit-message check)
uv run pre-commit install --install-hooks

# Quality gate, exactly what CI runs
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest

# Or use the Makefile
make install
make lint
make typecheck
make test
```

Run the services:

```bash
# FastAPI
uv run uvicorn app.api:app --reload --port 8000
curl http://127.0.0.1:8000/health

# Streamlit demo
uv run streamlit run app/demo_streamlit.py
```

Container:

```bash
docker build -t safesite-vision .
docker run --rm -p 8000:8000 safesite-vision
```

## Project structure

```
SafeSite-Vision/
├── app/                    # FastAPI service and Streamlit demo
├── configs/                # data, training, tracker and compliance-rule configs
├── data/                   # raw/interim/processed datasets (never committed)
├── docs/                   # architecture, datasets, model card, error analysis
├── models/                 # trained weights and exports (never committed)
├── notebooks/              # exploratory analysis
├── runs/                   # training and evaluation artefacts (never committed)
├── scripts/                # download, convert, split, train, evaluate, export, benchmark
├── src/safesite/           # library code
│   ├── data/               #   dataset tooling
│   ├── detection/          #   YOLO wrapper
│   ├── tracking/           #   ByteTrack integration
│   ├── association/        #   PPE-to-person association
│   ├── compliance/         #   rules, smoothing, events
│   ├── utils/              #   config, logging, geometry, IO
│   ├── pipeline.py         #   end-to-end orchestration
│   └── visualization.py    #   frame annotation
└── tests/                  # pytest suite
```

## Configuration

| File | Purpose |
| ---- | ------- |
| [`configs/data.yaml`](configs/data.yaml) | YOLO dataset paths and the fixed class order |
| [`configs/train_baseline.yaml`](configs/train_baseline.yaml) | Baseline training hyper-parameters |
| [`configs/tracker.yaml`](configs/tracker.yaml) | ByteTrack thresholds and track lifecycle |
| [`configs/compliance_rules.yaml`](configs/compliance_rules.yaml) | Equipment mapping, association, smoothing and rules |

## Roadmap

| Phase | Focus | Status |
| ----- | ----- | ------ |
| **0** | Foundation — repo scaffold, tooling, CI/CD, standards, branch protection | ✅ Done |
| **1** | Data pipeline — dataset registry and licences, download, YOLO conversion, dedup + leakage-free splits | ⏳ Planned |
| **2** | Detection baseline — train YOLO11n, evaluate mAP, error analysis, model card, ONNX export, FPS benchmark | ⏳ Planned |
| **3** | Tracking and association — ByteTrack integration, person track store, PPE-to-person matching | ⏳ Planned |
| **4** | Compliance engine — rule schema, zones, temporal smoothing, violation events | ⏳ Planned |
| **5** | Serving and demo — FastAPI endpoints, Streamlit demo, overlays, end-to-end smoke test | ⏳ Planned |
| **6** | Hardening and release — profiling, false-positive tuning, docs completion, `v1.0.0` | ⏳ Planned |

Each phase is tracked with a GitHub milestone; individual tasks live in the issue tracker.

## Contributing

Contributions are welcome. Read [`CONTRIBUTING.md`](CONTRIBUTING.md) first — it covers the
Issue → Branch → PR → Review → Squash-merge workflow, branch naming, Conventional Commits,
code style and the data/model rules.

- Bug reports and feature requests: use the issue templates.
- Security issues: **do not** open a public issue, follow [`SECURITY.md`](SECURITY.md).
- By participating you agree to the [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).

## Licence

This project is licensed under the **Apache License 2.0** — see [`LICENSE`](LICENSE).

> [!IMPORTANT]
> **Ultralytics dependency notice.** This project depends on
> [Ultralytics YOLO](https://github.com/ultralytics/ultralytics), which is licensed under
> **AGPL-3.0** (with a separate commercial/Enterprise licence available from Ultralytics).
> The Apache-2.0 licence above covers *this* repository's code only. If you redistribute or
> run a modified version of this project as a network service, the AGPL-3.0 obligations of
> the Ultralytics dependency may apply to you. Obtain an Ultralytics Enterprise licence if
> you need to avoid them.
>
> Datasets and trained weights carry their own licences; they are recorded in
> [`docs/datasets.md`](docs/datasets.md) and [`docs/model_card.md`](docs/model_card.md) and
> are **not** distributed from this repository.

## Contributors

| Contributor | Role |
| ----------- | ---- |
| [@MahdiMashayekhi-AI](https://github.com/MahdiMashayekhi-AI) | Maintainer — ML, MLOps, platform |
| [@Mohii722](https://github.com/Mohii722) | Maintainer — computer vision, evaluation |

See the [contributors graph](https://github.com/MahdiMashayekhi-AI/Safesite-Vision/graphs/contributors).
