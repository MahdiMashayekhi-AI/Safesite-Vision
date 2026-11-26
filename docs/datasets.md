# Datasets

Living record of every dataset used by SafeSite Vision. Update it in the same PR
that introduces a dataset.

## Rules

- Never commit dataset images, labels or archives to git (see `.gitignore`).
- Only use datasets whose licence allows both research and commercial use, or
  document the restriction explicitly and gate the code path accordingly.
- Record the exact licence, version/commit and download date for reproducibility.
- `scripts/download_data.py` must be able to reproduce `data/raw/` from scratch.

## Registry

| Dataset | Purpose | Images | Classes used | Licence | Commercial use | Source / version | Downloaded |
| ------- | ------- | ------ | ------------ | ------- | -------------- | ---------------- | ---------- |
| SH17 (local raw snapshot) | PPE detection | 8,099 | Mapping pending (#14) | Review pending (#12) | Not yet verified | Maintainer-provided files; versioned with DVC | Existing local import |

## Class mapping

Class ids are defined once in [`configs/data.yaml`](../configs/data.yaml) and must
stay stable across datasets.

| Class id | Name | Source label(s) |
| -------- | ---- | --------------- |
| 0 | person | _TBD_ |
| 1 | helmet | _TBD_ |
| 2 | no_helmet | _TBD_ |
| 3 | vest | _TBD_ |
| 4 | no_vest | _TBD_ |
| 5 | gloves | _TBD_ |
| 6 | no_gloves | _TBD_ |
| 7 | boots | _TBD_ |
| 8 | no_boots | _TBD_ |
| 9 | goggles | _TBD_ |
| 10 | no_goggles | _TBD_ |

## Splits

Describe how `scripts/dedup_split.py` produces `data/processed/ppe`:

- Deduplication strategy: _TBD_ (perceptual hash / embedding distance)
- Split ratios: _TBD_ (e.g. 70/15/15)
- Guarantee: no near-duplicate image appears in more than one split
- Leakage checks: same video/site must not span train and val

## Known issues

- _TBD_: class imbalance, small-object PPE, low-light footage, ...

## Local versioning and backup

The existing raw snapshot contains 8,099 files in each of `images`, `labels`,
`meta-data`, and `voc_labels`, plus the two original split lists. DVC tracks these
six outputs; Git stores only the corresponding `.dvc` pointers. Backing up this
snapshot does not complete the licence audit, download/checksum script, class
mapping, deduplication, or leakage checks tracked by Phase 1 issues.

See [data versioning](data_versioning.md) for the external backup, restore
commands, and a read-only full-object integrity verifier.
