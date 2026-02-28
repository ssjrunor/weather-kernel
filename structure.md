# Project Structure

## Goal
Keep the benchmark workflow compact and keep outputs standardized.

## Root
- `run.sh`
  - Primary entrypoint.
  - `./run.sh` for quick run.
  - `./run.sh full` for full run.

- `README.md`
  - Setup and usage.
  - Documents output file locations.

- `Makefile`
  - Build targets (`o0`, `o2`, `o3`, `native`).
  - Workflow targets:
    - `make quick`
    - `make benchmark`

## `src/`
- `src/stencil.c`, `src/stencil.h`
  - Core 2D 5-point stencil kernel + CLI.
- `src/timer.c`, `src/timer.h`
  - Monotonic timing helper.
- `src/checksum.c`, `src/checksum.h`
  - Checksum for correctness validation.

## `scripts/`
- `scripts/benchmark.py`
  - Single orchestrator script.
  - Builds binaries, runs the benchmark matrix, writes outputs.
  - Produces:
    - raw log
    - CSV
    - JSON
    - markdown summary
    - plots (optional, if matplotlib exists)

## `results/`
- `results/README.md`
  - Results folder guide.
- `results/raw/`
  - Raw run logs (`latest.log` + timestamped files).
- `results/processed/`
  - `latest_summary.md`
  - `latest_results.csv`
  - `latest_results.json`
  - timestamped copies of all outputs
- `results/figures/`
  - Optional plots (`*latest.png` + timestamped copies).

## `report/`
- `report/main.tex`, `report/references.bib`, `report/figures/`
  - Report assets for the larger project.
