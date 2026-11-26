# SH17 dataset versioning and backup

SafeSite Vision uses DVC to version dataset contents without putting images or
labels in Git. Python **3.12** and `uv sync --all-groups` install the DVC CLI.

## What belongs where

| Location | Contents | Version control |
| --- | --- | --- |
| `data/raw/images`, `labels`, `meta-data`, `voc_labels` | Original SH17 data | DVC |
| `data/raw/train_files.txt`, `val_files.txt` | Original split lists | DVC |
| `data/raw/*.dvc` | Content hashes and output metadata | Git |
| `.dvc/config`, `.dvcignore`, `.dvc/.gitignore` | Shared DVC settings | Git |
| `.dvc/config.local` | This computer's external-drive path | Local only |
| `.dvc/cache` | Local content-addressed object cache | Local only |
| `E:/Datasets/SH17` | External DVC object storage | External drive |

The existing loose dataset files and `archive.zip` on the external drive are
preserved. DVC stores its objects under `E:/Datasets/SH17/files/md5/`; it does not
replace those original files. Do not edit or rename DVC object files manually.

The raw dataset still needs a completed licence/provenance review under Issue
#12. Local backup does not imply permission to redistribute the dataset. This
setup does not publish dataset bytes to GitHub or cloud storage.

## Configure another clone or computer

Connect the drive, check that the directory exists, then run from the repository:

```powershell
uv sync --all-groups
uv run dvc remote add --local -d external-backup E:/Datasets/SH17
uv run dvc config --local cache.type copy
uv run dvc pull
```

If that remote already exists, update its local URL instead:

```powershell
uv run dvc remote modify --local external-backup url E:/Datasets/SH17
```

The local URL intentionally does not appear in the shared `.dvc/config`; other
contributors may use different drive letters. Their clone must configure a
reachable backup before running `dvc pull`. Do not share the drive as a public
remote until licensing and privacy requirements are resolved.

## Record and back up a dataset change

Work on an Issue branch, never directly on `main`:

```powershell
uv run dvc add data/raw/images data/raw/labels data/raw/meta-data data/raw/voc_labels data/raw/train_files.txt data/raw/val_files.txt
uv run dvc status
uv run dvc push -r external-backup -j 1
uv run dvc status --cloud -r external-backup
git add data/raw/images.dvc data/raw/labels.dvc data/raw/meta-data.dvc data/raw/voc_labels.dvc data/raw/train_files.txt.dvc data/raw/val_files.txt.dvc
git commit -m "chore(data): version the updated SH17 snapshot"
```

A single transfer worker avoids competing writes on the external HDD.

Push the branch and open a PR with the corresponding Issue reference. Only DVC
pointer/configuration files belong in that PR. The local cache uses copies so
editing a working image cannot silently change the cached backup object.

## Restore a recorded snapshot

1. Confirm there are no unrecorded dataset edits using `uv run dvc status`.
2. Switch Git to the branch or commit containing the desired `.dvc` pointers.
3. Connect the external drive and configure the local remote if necessary.
4. Run `uv run dvc pull -r external-backup` to retrieve the recorded objects.
5. Run `uv run dvc status` to check that the workspace matches the pointers.

`dvc push` backs up data; `git push` publishes only code and pointers. Both are
needed for recovery. Do not run `dvc gc` on the shared backup casually: old Git
revisions may still need objects that are not used by the current branch.

## Verification

`dvc status --cloud -r external-backup` checks whether the recorded objects are
present in the backup. Content integrity can also be independently checked by
hashing every object named by the `.dvc` pointers and their `.dir` manifests.
The setup report records the completed backup and integrity-check results.

```powershell
uv run python scripts/verify_dvc_backup.py --remote E:/Datasets/SH17
```
