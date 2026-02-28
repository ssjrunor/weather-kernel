/*
 * Weather Kernel (CS 3813)
 * File: src/checksum.h
 * Description: Interface for checksum validation of the final grid state.
 * Author: Oghenerunor Ewhro
 */
#ifndef CHECKSUM_H
#define CHECKSUM_H

/* Computes a deterministic checksum across all N x N cells. */
double compute_checksum(const double *grid, int n);

#endif
