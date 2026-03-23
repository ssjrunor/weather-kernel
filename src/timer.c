/*
 * Weather Kernel (CS 3813)
 * File: src/timer.c
 * Description: Monotonic timer implementation for stable elapsed timing.
 * Author: Oghenerunor Ewhro
 */
#include "timer.h"

#if defined(_WIN32)
#include <windows.h>
#else
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#endif

double now_seconds(void) {
#if defined(_WIN32)
    static LARGE_INTEGER frequency;
    static int initialized = 0;
    static int use_tickcount = 0;

    if (!initialized) {
        initialized = 1;
        if (!QueryPerformanceFrequency(&frequency)) {
            // Fallback: GetTickCount is monotonic (system uptime), resolution is ms.
            use_tickcount = 1;
        }
    }

    if (use_tickcount) {
        return (double)GetTickCount() / 1000.0;
    }

    LARGE_INTEGER counter;
    QueryPerformanceCounter(&counter);
    return (double)counter.QuadPart / (double)frequency.QuadPart;
#else
    struct timespec ts;
    /* CLOCK_MONOTONIC avoids time jumps from system clock adjustments. */
    if (clock_gettime(CLOCK_MONOTONIC, &ts) != 0) {
        perror("clock_gettime");
        exit(EXIT_FAILURE);
    }

    return (double)ts.tv_sec + (double)ts.tv_nsec * 1e-9;
#endif
}
