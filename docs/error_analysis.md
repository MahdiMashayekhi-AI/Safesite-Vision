# Error Analysis

Structured log of failure modes found during evaluation. Every entry should be
reproducible from a released checkpoint.

## How to run

1. Evaluate the checkpoint: `uv run python scripts/evaluate.py --weights <path>`
2. Inspect failures: `runs/` predictions and confusion matrix
3. Group failures by category below, with counts and example frame ids
4. Open an issue for any category representing > 2% of total errors

## Summary

| Category | Count | % of errors | Severity | Linked issue |
| -------- | ----- | ----------- | -------- | ------------ |
| _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ |

## Categories

### 1. Small / distant persons

- **Symptom:** PPE boxes on distant workers are missed.
- **Cause:** _TBD_
- **Mitigation:** _TBD_ (tiling, higher input resolution, SAHI)

### 2. Occlusion

- **Symptom:** _TBD_
- **Cause:** _TBD_
- **Mitigation:** _TBD_

### 3. Confusion between positive and negative PPE classes

- **Symptom:** `helmet` predicted where the label is `no_helmet`.
- **Cause:** _TBD_
- **Mitigation:** _TBD_

### 4. Association errors

- **Symptom:** PPE of person A attributed to person B in crowded frames.
- **Cause:** _TBD_
- **Mitigation:** _TBD_ (better association heuristic, pose keypoints)

### 5. Temporal flicker

- **Symptom:** single-frame violations reported repeatedly.
- **Cause:** unstable per-frame predictions.
- **Mitigation:** temporal smoothing window, cooldown.

### 6. Domain shift

- **Symptom:** recall drop on a new site/camera.
- **Cause:** _TBD_
- **Mitigation:** targeted labelling, fine-tuning

## Change log

| Date | Change |
| ---- | ------ |
| _TBD_ | Initial template |
