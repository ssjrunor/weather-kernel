/*
 * Weather Kernel (CS 3813)
 * File: src/timer.c
 * Description: POSIX monotonic timer implementation for stable elapsed timing.
 * Author: Oghenerunor Ewhro
 */
#include "timer.h"

#include <stdio.h>
#include <stdlib.h>
#include <time.h>

double now_seconds(void) {
    struct timespec ts;
    /* CLOCK_MONOTONIC avoids time jumps from system clock adjustments. */
    if (clock_gettime(CLOCK_MONOTONIC, &ts) != 0) {
        perror("clock_gettime");
        exit(EXIT_FAILURE);
    }

    return (double)ts.tv_sec + (double)ts.tv_nsec * 1e-9;
}
