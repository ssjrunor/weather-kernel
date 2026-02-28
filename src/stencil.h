/*
 * Weather Kernel (CS 3813)
 * File: src/stencil.h
 * Description: Shared constants and interfaces for the 2D 5-point stencil benchmark.
 * Author: Oghenerunor Ewhro
 */
#ifndef STENCIL_H
#define STENCIL_H

/* Default CLI parameters used when arguments are omitted. */
#define DEFAULT_N 512
#define DEFAULT_STEPS 100
#define DEFAULT_REPEATS 5

/* 5-point stencil weights: center + four orthogonal neighbors. */
#define STENCIL_WEIGHT_CENTER 0.50
#define STENCIL_WEIGHT_NEIGHBOR 0.125

/* Initializes the N x N grid deterministically for reproducible runs. */
void initialize_grid(double *grid, int n);

/* Runs the time-stepped stencil update and leaves the final state in a. */
void run_stencil(double *a, double *b, int n, int steps);

/* Parses a strictly positive integer; returns 0 on success, -1 on error. */
int parse_positive_int(const char *text, const char *name, int *out_value);

#endif
