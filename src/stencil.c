/*
 * Weather Kernel (CS 3813)
 * File: src/stencil.c
 * Description: CLI entry point and baseline 2D 5-point stencil implementation.
 * Author: Oghenerunor Ewhro
 */
#include "stencil.h"

#include "checksum.h"
#include "timer.h"

#include <errno.h>
#include <limits.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Prints valid CLI usage when too many arguments are provided. */
static void print_usage(const char *program_name) {
    fprintf(stderr, "Usage: %s [N] [steps] [repeats]\n", program_name);
}

/* Parses one positive integer argument with strict validation. */
int parse_positive_int(const char *text, const char *name, int *out_value) {
    char *end = NULL;
    long parsed = 0;

    errno = 0;
    parsed = strtol(text, &end, 10);
    if (errno != 0 || end == text || *end != '\0' || parsed <= 0 || parsed > INT_MAX) {
        fprintf(stderr, "Invalid %s value: %s\n", name, text);
        return -1;
    }

    *out_value = (int)parsed;
    return 0;
}

/*
 * Uses a deterministic integer mixing pattern so repeated runs with the same N
 * always start from the same data.
 */
void initialize_grid(double *grid, int n) {
    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            const unsigned mixed = ((unsigned)i * 1315423911u) ^ ((unsigned)j * 2654435761u);
            grid[(size_t)i * (size_t)n + (size_t)j] = (double)(mixed % 1000u) / 1000.0;
        }
    }
}

/*
 * Baseline 5-point stencil:
 * new(i,j) = wc * center + wn * (left + right + up + down)
 * Interior cells are updated; boundary cells remain fixed from initialization.
 */
void run_stencil(double *a, double *b, int n, int steps) {
    if (n < 3 || steps <= 0) {
        return;
    }

    const size_t cell_count = (size_t)n * (size_t)n;
    memcpy(b, a, cell_count * sizeof(double));

    double *src = a;
    double *dst = b;

    for (int step = 0; step < steps; ++step) {
        /* Update only interior points to avoid boundary checks in the hot loop. */
        for (int i = 1; i < n - 1; ++i) {
            const size_t row = (size_t)i * (size_t)n;
            for (int j = 1; j < n - 1; ++j) {
                const size_t idx = row + (size_t)j;
                dst[idx] = STENCIL_WEIGHT_CENTER * src[idx]
                           + STENCIL_WEIGHT_NEIGHBOR * (src[idx - 1] + src[idx + 1]
                                                        + src[idx - (size_t)n] + src[idx + (size_t)n]);
            }
        }

        double *tmp = src;
        src = dst;
        dst = tmp;
    }

    /* Ensure caller always reads the final data from array a. */
    if (src != a) {
        memcpy(a, src, cell_count * sizeof(double));
    }
}

int main(int argc, char **argv) {
    int n = DEFAULT_N;
    int steps = DEFAULT_STEPS;
    int repeats = DEFAULT_REPEATS;

    if (argc > 4) {
        print_usage(argv[0]);
        return EXIT_FAILURE;
    }

    /* Optional positional args: N, steps, repeats. */
    if (argc >= 2 && parse_positive_int(argv[1], "N", &n) != 0) {
        return EXIT_FAILURE;
    }
    if (argc >= 3 && parse_positive_int(argv[2], "steps", &steps) != 0) {
        return EXIT_FAILURE;
    }
    if (argc >= 4 && parse_positive_int(argv[3], "repeats", &repeats) != 0) {
        return EXIT_FAILURE;
    }

    const size_t n_size = (size_t)n;
    if (n_size > 0 && n_size > SIZE_MAX / n_size) {
        fprintf(stderr, "Grid size overflow for N=%d\n", n);
        return EXIT_FAILURE;
    }

    const size_t cell_count = n_size * n_size;
    if (cell_count > SIZE_MAX / sizeof(double)) {
        fprintf(stderr, "Allocation size overflow for N=%d\n", n);
        return EXIT_FAILURE;
    }

    /* Two buffers are used and swapped each step to avoid in-place hazards. */
    double *a = (double *)malloc(cell_count * sizeof(double));
    double *b = (double *)malloc(cell_count * sizeof(double));
    if (a == NULL || b == NULL) {
        fprintf(stderr, "Allocation failed for N=%d\n", n);
        free(a);
        free(b);
        return EXIT_FAILURE;
    }

    double total_time = 0.0;
    for (int r = 0; r < repeats; ++r) {
        /* Reinitialize each repeat so timing compares identical workloads. */
        initialize_grid(a, n);

        const double start = now_seconds();
        run_stencil(a, b, n, steps);
        const double end = now_seconds();

        total_time += (end - start);
    }

    const double avg_time = total_time / (double)repeats;
    /* Checksum helps detect accidental correctness regressions. */
    const double checksum = compute_checksum(a, n);

    printf("RESULT N=%d steps=%d repeats=%d avg_time_s=%.9f checksum=%.12e\n",
           n, steps, repeats, avg_time, checksum);

    free(a);
    free(b);
    return EXIT_SUCCESS;
}
