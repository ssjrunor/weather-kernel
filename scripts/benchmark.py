#!/usr/bin/env python3
"""
Weather Kernel (CS 3813)
File: scripts/benchmark.py
Description: Benchmark runner that builds binaries, executes runs,
             and exports structured results.
Author: Oghenerunor Ewhro
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import shutil
import statistics
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "results" / "raw"
PROCESSED_DIR = ROOT / "results" / "processed"
FIG_DIR = ROOT / "results" / "figures"

RESULT_RE = re.compile(
    r"RESULT\s+"
    r"N=(?P<N>\d+)\s+"
    r"steps=(?P<steps>\d+)\s+"
    r"repeats=(?P<repeats>\d+)\s+"
    r"avg_time_s=(?P<avg_time_s>[-+0-9.eE]+)\s+"
    r"checksum=(?P<checksum>[-+0-9.eE]+)"
)

DEFAULT_BUILDS = ["o0", "o2", "o3", "native"]
DEFAULT_SIZES = [128, 256, 512, 1024, 2048]
QUICK_SIZES = [128, 256, 512]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run stencil benchmarks and export structured results."
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Use smaller inputs for faster turnaround.",
    )
    parser.add_argument(
        "--sizes",
        type=str,
        default="",
        help="Comma-separated grid sizes (example: 128,256,512).",
    )
    parser.add_argument("--steps", type=int, default=200, help="Stencil time steps per run.")
    parser.add_argument("--repeats", type=int, default=5, help="Timed repeats per run.")
    parser.add_argument(
        "--builds",
        type=str,
        default=",".join(DEFAULT_BUILDS),
        help="Comma-separated build targets from Makefile (example: o0,o2,o3,native).",
    )
    parser.add_argument(
        "--skip-plots",
        action="store_true",
        help="Skip plotting even if matplotlib is installed.",
    )
    parser.add_argument(
        "--clear-results",
        action="store_true",
        help="Delete existing files in results/raw, results/processed, and results/figures before running.",
    )
    parser.add_argument(
        "--clear-only",
        action="store_true",
        help="Delete existing result files and exit without running benchmarks.",
    )
    return parser.parse_args()


def parse_int_list(raw: str) -> list[int]:
    values: list[int] = []
    for item in raw.split(","):
        text = item.strip()
        if not text:
            continue
        value = int(text)
        if value <= 0:
            raise ValueError("all list values must be positive integers")
        values.append(value)
    if not values:
        raise ValueError("list cannot be empty")
    return values


def parse_text_list(raw: str) -> list[str]:
    values = [item.strip() for item in raw.split(",") if item.strip()]
    if not values:
        raise ValueError("list cannot be empty")
    return values


def run_command(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


def ensure_directories() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)


def clear_result_artifacts() -> int:
    removed_count = 0
    for directory in (RAW_DIR, PROCESSED_DIR, FIG_DIR):
        if not directory.exists():
            continue
        for entry in directory.iterdir():
            if entry.is_file() or entry.is_symlink():
                entry.unlink()
                removed_count += 1
            elif entry.is_dir():
                shutil.rmtree(entry)
                removed_count += 1
    return removed_count


def build_binaries(builds: list[str]) -> None:
    for build in builds:
        result = run_command(["make", build], ROOT)
        if result.returncode != 0:
            print(f"[ERROR] Build failed for target: {build}", file=sys.stderr)
            if result.stdout:
                print(result.stdout, file=sys.stderr)
            if result.stderr:
                print(result.stderr, file=sys.stderr)
            raise SystemExit(1)
        print(f"[OK] Built target: {build}")


def run_benchmark(
    build: str,
    n: int,
    steps: int,
    repeats: int,
) -> dict[str, str]:
    binary = ROOT / "bin" / f"stencil_{build}"
    result = run_command([str(binary), str(n), str(steps), str(repeats)], ROOT)
    if result.returncode != 0:
        print(f"[ERROR] Benchmark command failed: {binary}", file=sys.stderr)
        if result.stdout:
            print(result.stdout, file=sys.stderr)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        raise SystemExit(1)

    line = result.stdout.strip().splitlines()[-1] if result.stdout.strip() else ""
    match = RESULT_RE.search(line)
    if not match:
        print(f"[ERROR] Unexpected program output for build={build}, N={n}: {line}", file=sys.stderr)
        raise SystemExit(1)

    row = match.groupdict()
    row["build"] = build
    return row


def write_csv(rows: list[dict[str, str]], timestamp: str) -> tuple[Path, Path]:
    csv_name = f"results_{timestamp}.csv"
    csv_path = PROCESSED_DIR / csv_name
    latest_path = PROCESSED_DIR / "latest_results.csv"

    fieldnames = ["run_timestamp", "build", "N", "steps", "repeats", "avg_time_s", "checksum"]
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "run_timestamp": timestamp,
                    "build": row["build"],
                    "N": row["N"],
                    "steps": row["steps"],
                    "repeats": row["repeats"],
                    "avg_time_s": row["avg_time_s"],
                    "checksum": row["checksum"],
                }
            )

    shutil.copyfile(csv_path, latest_path)
    return csv_path, latest_path


def write_json(rows: list[dict[str, str]], timestamp: str) -> tuple[Path, Path]:
    json_path = PROCESSED_DIR / f"results_{timestamp}.json"
    latest_path = PROCESSED_DIR / "latest_results.json"

    payload = {
        "run_timestamp": timestamp,
        "rows": [
            {
                "build": row["build"],
                "N": int(row["N"]),
                "steps": int(row["steps"]),
                "repeats": int(row["repeats"]),
                "avg_time_s": float(row["avg_time_s"]),
                "checksum": float(row["checksum"]),
            }
            for row in rows
        ],
    }

    with json_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")

    shutil.copyfile(json_path, latest_path)
    return json_path, latest_path


def write_raw_log(log_lines: list[str], timestamp: str) -> tuple[Path, Path]:
    log_path = RAW_DIR / f"benchmark_{timestamp}.log"
    latest_path = RAW_DIR / "latest.log"
    with log_path.open("w", encoding="utf-8") as handle:
        handle.write("\n".join(log_lines))
        handle.write("\n")
    shutil.copyfile(log_path, latest_path)
    return log_path, latest_path


def almost_equal(a: float, b: float) -> bool:
    return math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-12)


def find_checksum_warnings(rows: list[dict[str, str]]) -> list[str]:
    by_n: dict[str, list[tuple[str, float]]] = {}
    for row in rows:
        by_n.setdefault(row["N"], []).append((row["build"], float(row["checksum"])))

    warnings: list[str] = []
    for n in sorted(by_n, key=int):
        values = by_n[n]
        if not values:
            continue
        baseline = values[0][1]
        bad_builds = [build for build, checksum in values if not almost_equal(checksum, baseline)]
        if bad_builds:
            warnings.append(
                f"N={n}: checksum mismatch in builds {', '.join(sorted(bad_builds))}"
            )
    return warnings


def create_runtime_tables(rows: list[dict[str, str]], builds: list[str]) -> tuple[list[str], list[str], str]:
    by_n: dict[int, dict[str, float]] = {}
    by_build: dict[str, list[float]] = {build: [] for build in builds}
    for row in rows:
        n = int(row["N"])
        build = row["build"]
        runtime = float(row["avg_time_s"])
        by_n.setdefault(n, {})[build] = runtime
        by_build.setdefault(build, []).append(runtime)

    grid_lines = ["| N | " + " | ".join(builds) + " | Fastest |", "|---|" + "|".join(["---"] * (len(builds) + 1)) + "|"]
    for n in sorted(by_n):
        values = by_n[n]
        fastest_build = min(values, key=values.get)
        row_cells = [f"{n}"]
        for build in builds:
            row_cells.append(f"{values.get(build, float('nan')):.6f}" if build in values else "-")
        row_cells.append(f"{fastest_build} ({values[fastest_build]:.6f}s)")
        grid_lines.append("| " + " | ".join(row_cells) + " |")

    rank_lines = ["| Build | Mean runtime (s) | Speedup vs o0 |", "|---|---:|---:|"]
    o0_mean = statistics.fmean(by_build["o0"]) if by_build.get("o0") else float("nan")
    mean_by_build = [
        (build, statistics.fmean(runtimes))
        for build, runtimes in by_build.items()
        if runtimes
    ]
    mean_by_build.sort(key=lambda item: item[1])
    fastest_overall = mean_by_build[0][0] if mean_by_build else ""

    for build, mean_runtime in mean_by_build:
        if math.isnan(o0_mean):
            speedup = "n/a"
        else:
            speedup = f"{(o0_mean / mean_runtime):.2f}x"
        rank_lines.append(f"| {build} | {mean_runtime:.6f} | {speedup} |")

    return grid_lines, rank_lines, fastest_overall


def write_summary(
    rows: list[dict[str, str]],
    builds: list[str],
    sizes: list[int],
    steps: int,
    repeats: int,
    timestamp: str,
    csv_latest: Path,
    json_latest: Path,
    log_latest: Path,
    plot_paths: list[Path],
) -> tuple[Path, Path]:
    warnings = find_checksum_warnings(rows)
    grid_lines, rank_lines, fastest_overall = create_runtime_tables(rows, builds)
    summary_path = PROCESSED_DIR / f"summary_{timestamp}.md"
    latest_path = PROCESSED_DIR / "latest_summary.md"

    plot_text = "\n".join(f"- `{path.relative_to(ROOT)}`" for path in plot_paths) if plot_paths else "- (no plots generated)"
    warning_text = "\n".join(f"- {item}" for item in warnings) if warnings else "- None"

    content = f"""# Weather Kernel Benchmark Summary

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Run Settings
- Builds: {", ".join(builds)}
- Grid sizes (N): {", ".join(str(n) for n in sizes)}
- Steps: {steps}
- Repeats: {repeats}

## Primary Output Files
- `{csv_latest.relative_to(ROOT)}`
- `{json_latest.relative_to(ROOT)}`
- `{latest_path.relative_to(ROOT)}`
- `{log_latest.relative_to(ROOT)}`

## Quick Takeaway
- Fastest build by mean runtime: **{fastest_overall or "n/a"}**

## Runtime By Grid Size (seconds)
{chr(10).join(grid_lines)}

## Build Ranking (lower is better)
{chr(10).join(rank_lines)}

## Correctness Check
Checksum mismatches across builds:
{warning_text}

## Generated Plots
{plot_text}
"""

    with summary_path.open("w", encoding="utf-8") as handle:
        handle.write(content)

    shutil.copyfile(summary_path, latest_path)
    return summary_path, latest_path


def generate_plots(
    rows: list[dict[str, str]],
    builds: list[str],
    timestamp: str,
) -> list[Path]:
    try:
        import matplotlib.pyplot as plt  # type: ignore
    except Exception:
        print("[INFO] matplotlib not found. Skipping plots.")
        return []

    by_build: dict[str, list[float]] = {build: [] for build in builds}
    by_n: dict[str, dict[int, float]] = {build: {} for build in builds}
    for row in rows:
        build = row["build"]
        n = int(row["N"])
        t = float(row["avg_time_s"])
        by_build.setdefault(build, []).append(t)
        by_n.setdefault(build, {})[n] = t

    output_paths: list[Path] = []

    mean_times = [statistics.fmean(by_build[build]) for build in builds if by_build.get(build)]
    mean_builds = [build for build in builds if by_build.get(build)]
    plt.figure(figsize=(8, 4.5))
    plt.bar(mean_builds, mean_times)
    plt.xlabel("Build")
    plt.ylabel("Average Runtime (s)")
    plt.title("Runtime vs Optimization")
    plt.tight_layout()
    plot1 = FIG_DIR / f"runtime_vs_optimization_{timestamp}.png"
    plot1_latest = FIG_DIR / "runtime_vs_optimization_latest.png"
    plt.savefig(plot1, dpi=200)
    plt.close()
    shutil.copyfile(plot1, plot1_latest)
    output_paths.extend([plot1, plot1_latest])

    plt.figure(figsize=(8, 4.5))
    for build in builds:
        pairs = sorted(by_n.get(build, {}).items())
        if not pairs:
            continue
        xs = [n for n, _ in pairs]
        ys = [t for _, t in pairs]
        plt.plot(xs, ys, marker="o", label=build)
    plt.xlabel("Grid Size (N)")
    plt.ylabel("Average Runtime (s)")
    plt.title("Runtime vs Grid Size")
    plt.legend()
    plt.tight_layout()
    plot2 = FIG_DIR / f"runtime_vs_grid_size_{timestamp}.png"
    plot2_latest = FIG_DIR / "runtime_vs_grid_size_latest.png"
    plt.savefig(plot2, dpi=200)
    plt.close()
    shutil.copyfile(plot2, plot2_latest)
    output_paths.extend([plot2, plot2_latest])

    return output_paths


def main() -> None:
    args = parse_args()

    ensure_directories()

    if args.clear_results or args.clear_only:
        removed_count = clear_result_artifacts()
        print(f"[INFO] Cleared {removed_count} result artifact(s).")

    if args.clear_only:
        print("[INFO] Clear-only mode complete.")
        return

    if args.steps <= 0 or args.repeats <= 0:
        raise SystemExit("steps and repeats must be positive")

    try:
        if args.sizes.strip():
            sizes = parse_int_list(args.sizes)
        else:
            sizes = QUICK_SIZES if args.quick else DEFAULT_SIZES
        builds = parse_text_list(args.builds)
    except ValueError as exc:
        raise SystemExit(f"invalid argument: {exc}") from exc
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    build_binaries(builds)

    rows: list[dict[str, str]] = []
    log_lines: list[str] = []

    print("[INFO] Running benchmark matrix...")
    for build in builds:
        for n in sizes:
            row = run_benchmark(build, n, args.steps, args.repeats)
            rows.append(row)
            line = (
                f"build={build} RESULT N={row['N']} steps={row['steps']} "
                f"repeats={row['repeats']} avg_time_s={row['avg_time_s']} "
                f"checksum={row['checksum']}"
            )
            log_lines.append(line)
            print(f"[OK] {line}")

    csv_path, csv_latest = write_csv(rows, timestamp)
    json_path, json_latest = write_json(rows, timestamp)
    log_path, log_latest = write_raw_log(log_lines, timestamp)

    plot_paths: list[Path] = []
    if not args.skip_plots:
        plot_paths = generate_plots(rows, builds, timestamp)

    summary_path, summary_latest = write_summary(
        rows=rows,
        builds=builds,
        sizes=sizes,
        steps=args.steps,
        repeats=args.repeats,
        timestamp=timestamp,
        csv_latest=csv_latest,
        json_latest=json_latest,
        log_latest=log_latest,
        plot_paths=plot_paths,
    )

    print("\nDone. See files:")
    print(f"- {summary_latest.relative_to(ROOT)}")
    print(f"- {csv_latest.relative_to(ROOT)}")
    print(f"- {json_latest.relative_to(ROOT)}")
    print("\nTimestamped artifacts:")
    print(f"- {summary_path.relative_to(ROOT)}")
    print(f"- {csv_path.relative_to(ROOT)}")
    print(f"- {json_path.relative_to(ROOT)}")
    print(f"- {log_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
