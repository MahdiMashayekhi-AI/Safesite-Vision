# Model Card — SafeSite Vision PPE Detector

Template based on the Model Cards for Model Reporting paper (Mitchell et al., 2019).
Fill in one card per released model version.

## Model details

| Field | Value |
| ----- | ----- |
| Version | _TBD_ |
| Architecture | _TBD_ (e.g. YOLO11n) |
| Checkpoint | _TBD_ (release asset, never committed to git) |
| Training date | _TBD_ |
| Trained by | _TBD_ |
| Licence | _TBD_ (weights) |
| Framework | Ultralytics _TBD_ |

## Intended use

- **Primary use:** detecting PPE compliance of persons in workplace video.
- **Intended users:** safety officers and researchers evaluating PPE pipelines.
- **Out of scope:** legal evidence, disciplinary decisions without human review,
  surveillance of individuals outside the site, identity recognition.

## Training data

- Datasets: see [`datasets.md`](datasets.md).
- Splits, deduplication and leakage controls: see [`datasets.md`](datasets.md).
- Known biases: _TBD_ (site type, lighting, camera angle, PPE colour, ...).

## Evaluation

| Metric | Value | Notes |
| ------ | ----- | ----- |
| mAP50 | _TBD_ | |
| mAP50-95 | _TBD_ | |
| Precision | _TBD_ | |
| Recall | _TBD_ | |
| Per-class mAP50 | _TBD_ | weakest classes: _TBD_ |
| FPS (CPU) | _TBD_ | |

Evaluation protocol and scripts: `scripts/evaluate.py`, `scripts/benchmark_fps.py`.

## Limitations

- _TBD_

## Ethical considerations

- PPE decisions affect workers; a human must review any consequence.
- Frames may contain identifiable people: retention and access must be controlled.
- The model inherits the licence terms of its base weights and training data.

## Maintenance

- Owner: _TBD_
- Retraining trigger: _TBD_ (drift, new PPE type, recall drop below _TBD_)
- Last review: _TBD_
