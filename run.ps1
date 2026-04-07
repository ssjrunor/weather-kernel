
# Weather Kernel (CS 3813)
# File: run.ps1
# Description: PowerShell wrapper for running benchmark modes (quick, full, or clear-only).
# Author: Cedrick TAHMO

# Accept a benchmark mode parameter with validation
param(
  [ValidateSet("quick", "full", "clear")]
  [string]$Mode = "quick"
)

# Execute the appropriate benchmark mode
switch ($Mode) {
  "quick" {
    # Run a quick benchmark with reduced dataset
    python scripts/benchmark.py --quick
    break
  }
  "full" {
    # Run a full benchmark with complete dataset
    python scripts/benchmark.py
    break
  }
  "clear" {
    # Clear previous benchmark results only
    python scripts/benchmark.py --clear-only
    break
  }
  default {
    Write-Host "Usage: ./run.ps1 -Mode quick|full|clear"
    exit 1
  }
}
