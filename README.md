# Weather Kernel (CS 3813)

This repository contains a stencil-kernel benchmarking tool. It compiles multiple optimization builds of the same C kernel, runs them under a configurable workload, and exports results as markdown, CSV, JSON, and optional plots.

## Purpose
Use this to know:
- Which build (`o0`, `o2`, `o3`, `native`) is fastest for your workload.
- Whether faster results still correct.
- How runtime change as grid size grows.

The correctness check is checksum-based. For the same workload (`N`, `steps`, `repeats`), checksums should match across builds.

## What The Program Does
1. Builds selected binaries.
2. Runs each binary for each selected grid size.
3. Captures runtime and checksum from each run.
4. Writes:
- `results/processed/latest_summary.md`
- `results/processed/latest_results.csv`
- `results/processed/latest_results.json`
- `results/raw/latest.log`
- optional latest plots in `results/figures/`
5. Writes timestamped copies for history.

## Requirements
- C compiler with C11 support (`cc`, `clang`, or `gcc`)
- GNU Make
- Python 3
- Optional: `matplotlib` for plot generation (`.png`)

## Quick Start
Run the default quick benchmark:

```bash
./run.sh
```

Equivalent:

```bash
make quick
```

Clear old result artifacts only:

```bash
./run.sh clear
# or
make clear-results
```

## User-Facing Controls

### 1) Wrapper Script Modes
Command:

```bash
./run.sh [quick|full|clear]
```

| Mode | Default? | What it does | Impact |
|---|---|---|---|
| `quick` | Yes | Runs `scripts/benchmark.py --quick` | Fastest feedback, smaller workload (`N=128,256,512`) |
| `full` | No | Runs `scripts/benchmark.py` with default full sizes | Better coverage (`N` up to `2048`), longer runtime |
| `clear` | No | Runs `scripts/benchmark.py --clear-only` | Deletes existing result files without running benchmark |

### 2) Python CLI Options (Primary Control Surface)
Command:

```bash
python3 scripts/benchmark.py [options]
```

| Option | Default | Valid values | What it controls | Impact |
|---|---:|---|---|---|
| `--quick` | off | flag | Chooses quick size preset if `--sizes` is not set | Reduces run time by using smaller grids |
| `--sizes` | preset from mode | comma-separated positive ints, e.g. `256,512,1024` | Exact grid sizes to benchmark | Larger `N` increases runtime and memory strongly |
| `--steps` | `200` | positive int | Time-step count per run | Runtime grows roughly linearly with `steps` |
| `--repeats` | `5` | positive int | Number of timed repetitions per point | Runtime grows linearly; higher repeats improve timing stability |
| `--builds` | `o0,o2,o3,native` | comma-separated Make targets | Which build variants to include | More builds increase run time proportionally |
| `--skip-plots` | off | flag | Skips matplotlib plot generation | Slightly faster post-processing; no PNG figures |
| `--clear-results` | off | flag | Clears old artifacts before running | Prevents mixing old/new files |
| `--clear-only` | off | flag | Clears old artifacts and exits | Cleanup only, no benchmark run |

Notes:
- `--sizes` overrides quick/full presets.
- `--builds` values must correspond to valid Make targets; standard options are `o0`, `o2`, `o3`, `native`.
- `--steps` and `--repeats` must be positive integers.

### 3) Direct Binary Parameters
Build first:

```bash
make o3
```

Run:

```bash
bin/stencil_o3 [N] [steps] [repeats]
```

| Parameter | Default (binary mode) | Valid values | Impact |
|---|---:|---|---|
| `N` | `512` | positive int | Grid dimension (`N x N`) | Largest performance driver; compute and memory scale ~`N^2` |
| `steps` | `100` | positive int | Number of stencil updates | Runtime scales roughly linearly with `steps` |
| `repeats` | `5` | positive int | Number of timed repeats | Runtime scales linearly; average becomes less noisy |

Important:
- In direct binary mode, default `steps` is `100`.
- In benchmark script mode, default `steps` is `200`.
- Keep this distinction in mind when comparing results.

### 4) Make Variables (User-Overridable)
You can override these at runtime:

```bash
CC=clang make benchmark
PYTHON=python3.12 make quick
```

| Variable | Default | Impact |
|---|---|---|
| `CC` | `cc` | Changes compiler used for all builds; can affect both speed and checksum stability in edge cases |
| `PYTHON` | `python3` | Chooses Python interpreter used by Make targets |

## Build Profiles And Expected Behavior
| Build tag | Compiler flags | Typical behavior |
|---|---|---|
| `o0` | `-O0` | Baseline with minimal optimization; usually slowest |
| `o2` | `-O2` | Strong general optimization; often best speed/consistency tradeoff |
| `o3` | `-O3` | More aggressive optimization; may be faster or similar to `o2` |
| `native` | `-O3 -march=native` (fallback `-mcpu=native`) | Tuned to current machine CPU; often fastest on host, less portable |

## Workload Size And Runtime Impact
Approximate runtime scaling per run matrix:

`total_runtime ~ (#builds) * (#sizes) * repeats * steps * N^2`

Interpretation:
- Doubling `N` can increase compute cost by about 4x.
- Doubling `steps` roughly doubles runtime.
- Doubling `repeats` roughly doubles runtime.
- Adding more builds increases runtime proportionally.

Practical guidance:
- Use `quick` for frequent iteration.
- Use larger `N` and higher `repeats` for final comparisons.
- Keep parameters identical when comparing builds.

## Output Files And How To Use Them

### Primary files
- `results/processed/latest_summary.md`
  - Human-readable decision file.
- `results/processed/latest_results.csv`
  - Spreadsheet-friendly table.
- `results/processed/latest_results.json`
  - Structured machine-readable output.
- `results/raw/latest.log`
  - Raw line output from benchmark runs.

### Timestamped history
Each run also writes timestamped files such as:
- `results/processed/results_YYYYMMDD_HHMMSS.csv`
- `results/processed/summary_YYYYMMDD_HHMMSS.md`
- `results/raw/benchmark_YYYYMMDD_HHMMSS.log`

### CSV/JSON schema
Each row contains:
- `run_timestamp`: timestamp key for that run
- `build`: build variant
- `N`: grid size
- `steps`: step count
- `repeats`: repeat count
- `avg_time_s`: average runtime in seconds (lower is better)
- `checksum`: deterministic correctness signal

## Result Interpretation Guide

### 1) Confirm correctness first
In `latest_summary.md`, check `Correctness Check`.
- Expected: `None` mismatches.
- If mismatches appear, treat performance comparisons as invalid until fixed.

### 2) Identify fastest build for your use case
Use:
- `Runtime By Grid Size` to find best build for each `N`.
- `Build Ranking` to find best mean performer across tested sizes.

### 3) Understand speedup values
Speedup is reported relative to `o0`:
- `2.00x` means twice as fast as `o0`.
- Higher is better.

### 4) Compare only like-for-like rows
Valid comparisons require same:
- `N`
- `steps`
- `repeats`
- same machine/environment

## Recommended Workflows

### Fast local check
```bash
./run.sh
```

### Full benchmark from clean results directory
```bash
python3 scripts/benchmark.py --clear-results
```

### Custom experiment matrix
```bash
python3 scripts/benchmark.py \
  --clear-results \
  --sizes 256,512,1024,1536 \
  --steps 300 \
  --repeats 7 \
  --builds o2,o3,native
```

### Compare one binary manually
```bash
make o3
bin/stencil_o3 1024 300 10
```

## Troubleshooting
- `invalid argument` errors:
  - Ensure `--sizes` values are positive integers and comma-separated.
  - Ensure `--steps` and `--repeats` are positive.
- Build failure for a build tag:
  - Ensure tag exists in Makefile (`o0`, `o2`, `o3`, `native`).
  - Check compiler availability (`cc --version`).
- No plots generated:
  - Install `matplotlib`, or omit plots intentionally with `--skip-plots`.

## Reproducibility Best Practices
- Keep machine power mode fixed.
- Close heavy background workloads.
- Keep benchmark parameters fixed across comparisons.
- Increase `repeats` to reduce timing noise.
- Use `--clear-results` before formal runs to avoid stale artifacts.

## Author
- Oghenerunor Ewhro
