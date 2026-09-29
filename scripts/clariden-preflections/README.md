# Clariden preflection helpers

Migrated from `/users/xccyn/mrd-local-qwen` and `/users/xccyn/.edf/mrd-sglang.toml` on 2026-09-29. The canonical source is now this directory in `/capstor/store/cscs/swissai/ab023/xccyn/spsd/model-raising-data`.

Run helpers with `uv run python scripts/clariden-preflections/<script>.py` from the repository root after `uv sync`. Jobs use that repository and the `mrd-sglang.toml` in this directory. Credentials stay in the existing home-directory credential files.

Generated documents, preflections, sidecars, model weights, container image, and caches remain at their existing `/iopsstor/scratch/cscs/xccyn/` locations. In particular, the 2,000-row thinking and non-thinking results remain under `mrd-local-qwen/bench` and `mrd-local-qwen/bench_nothink`. Migration does not regenerate or modify them.

## Historical jobs

The numbered scripts in `jobs/` record earlier setup, generation, and analysis operations. They are not an ordered recipe to rerun: some overwrite sidecars or derived datasets, and others submit generation jobs against existing output directories. None were submitted during migration. Review input/output paths before running one. Create `scripts/clariden-preflections/logs/` before submitting a job; historical logs are preserved unchanged there and ignored by Git.

| Jobs | Operation |
| --- | --- |
| 01–03 | Build container, set up Python environment, download model; job 02 also writes the mini sidecar |
| 04–06 | Generate or submit 20-document comparison runs; job 04 also rewrites the mini sidecar |
| 07–08 | Write clipped source documents and recomputed-position comparison data |
| 09 | Overwrite the 4,000-row benchmark sidecar |
| 10–12 | Submit thinking/non-thinking generation runs |
| 13–15 | Write comparison data, thinking analysis, and the viewer corpus |

`build_corpus.py` defaults to 1,000 rows; use `--n 2000` to export the full thinking run. `recompute_positions.py` and `rebuild_data.py` write derived files without editing original generation results. Existing job 01 tolerates a failed container-build command when an image file exists; inspect its output before trusting a rebuilt image.
