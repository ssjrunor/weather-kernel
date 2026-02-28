# Weather Kernel (CS 3813)
# File: Makefile
# Description: Build and benchmark entrypoints.
# Author: Oghenerunor Ewhro

CC ?= cc
PYTHON ?= python3
CFLAGS_COMMON := -std=c11 -Wall -Wextra -Wpedantic -D_POSIX_C_SOURCE=200809L
SRC := src/stencil.c src/timer.c src/checksum.c
BIN_DIR := bin

.PHONY: all help o0 o2 o3 native quick benchmark clear-results clean

all: o3

help:
	@echo "Weather Kernel commands:"
	@echo "  make quick      # Fast benchmark run"
	@echo "  make benchmark  # Full benchmark run"
	@echo "  make clear-results"
	@echo "  make o0|o2|o3|native"
	@echo "  make clean"

$(BIN_DIR):
	mkdir -p $(BIN_DIR)

# Baseline no optimization.
$(BIN_DIR)/stencil_o0: $(SRC) | $(BIN_DIR)
	$(CC) $(CFLAGS_COMMON) -O0 $(SRC) -o $@

# Typical release optimization.
$(BIN_DIR)/stencil_o2: $(SRC) | $(BIN_DIR)
	$(CC) $(CFLAGS_COMMON) -O2 $(SRC) -o $@

# Aggressive optimization.
$(BIN_DIR)/stencil_o3: $(SRC) | $(BIN_DIR)
	$(CC) $(CFLAGS_COMMON) -O3 $(SRC) -o $@

# Host-specific optimization with portable fallback for compilers that
# prefer -mcpu=native over -march=native.
$(BIN_DIR)/stencil_native: $(SRC) | $(BIN_DIR)
	@$(CC) $(CFLAGS_COMMON) -O3 -march=native $(SRC) -o $@ 2>/dev/null || \
	$(CC) $(CFLAGS_COMMON) -O3 -mcpu=native $(SRC) -o $@

o0: $(BIN_DIR)/stencil_o0

o2: $(BIN_DIR)/stencil_o2

o3: $(BIN_DIR)/stencil_o3

native: $(BIN_DIR)/stencil_native

quick:
	$(PYTHON) scripts/benchmark.py --quick

benchmark:
	$(PYTHON) scripts/benchmark.py

clear-results:
	$(PYTHON) scripts/benchmark.py --clear-only

clean:
	rm -rf $(BIN_DIR)
	rm -f *.o *.out
