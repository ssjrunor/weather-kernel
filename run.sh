#!/usr/bin/env bash
# Weather Kernel (CS 3813)
# File: run.sh
# Description: Primary benchmark entrypoint.
# Author: Oghenerunor Ewhro

set -euo pipefail

mode="${1:-quick}"

case "${mode}" in
    quick)
        python3 scripts/benchmark.py --quick
        ;;
    full)
        python3 scripts/benchmark.py
        ;;
    clear)
        python3 scripts/benchmark.py --clear-only
        ;;
    *)
        echo "Usage: ./run.sh [quick|full|clear]"
        exit 1
        ;;
esac
