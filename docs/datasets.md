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
| _TBD_   | _TBD_   | _TBD_  | _TBD_        | _TBD_   | _TBD_          | _TBD_            | _TBD_      |

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
