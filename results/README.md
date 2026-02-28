# Results Folder Guide

This folder contains exported benchmark outputs.

## Primary Files
- `processed/latest_summary.md`:
  - benchmark summary.
  - Includes runtime tables and fastest build.
- `processed/latest_results.csv`:
  - CSV results table.
  - Open in Excel, Google Sheets, or Numbers.
- `processed/latest_results.json`:
  - Same data in JSON format for pipelines/tools.

## Other Files
- `raw/latest.log`:
  - Raw program output captured during the latest run.
- `figures/*latest.png`:
  - Latest plots (if matplotlib is installed).

## Note
Timestamped files (for run history) are also written next to each `latest_*` file.
