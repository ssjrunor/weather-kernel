/*
 * Weather Kernel (CS 3813)
 * File: src/checksum.c
 * Description: Kahan-style floating-point summation for stable checksums.
 * Author: Oghenerunor Ewhro
 */
#include "checksum.h"
#include <stddef.h>

double compute_checksum(const double *grid, int n) {
    const size_t count = (size_t)n * (size_t)n;
    double sum = 0.0;
    double correction = 0.0;

    /* Compensated summation reduces error drift across large grids. */
    for (size_t i = 0; i < count; ++i) {
        const double value = grid[i] - correction;
        const double next_sum = sum + value;
        correction = (next_sum - sum) - value;
        sum = next_sum;
    }

    return sum;
}
