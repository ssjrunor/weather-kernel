@echo off
setlocal
set "CC=gcc"

rem Weather Kernel (CS 3813)
rem File: run.bat
rem Description: Batch wrapper for running benchmark modes (quick, full, or clear-only).
rem Usage: run.bat [quick|full|clear]
rem Author: Cedrick TAHMO

rem Get the first argument or default to "quick"
set "mode=%~1"
if "%mode%"=="" set "mode=quick"

rem Execute the appropriate benchmark mode
if /I "%mode%"=="quick" (
  rem Run a quick benchmark with reduced dataset
  python scripts\benchmark.py --quick
) else if /I "%mode%"=="full" (
  rem Run a full benchmark with complete dataset
  python scripts\benchmark.py
) else if /I "%mode%"=="clear" (
  rem Clear previous benchmark results only
  python scripts\benchmark.py --clear-only
) else (
  rem Invalid mode - show usage
  echo Usage: run.bat [quick^|full^|clear]
  exit /b 1
)

endlocal