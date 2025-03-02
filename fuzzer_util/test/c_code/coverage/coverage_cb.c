#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>
#include <sys/file.h>

static uint32_t total_guards = 0;
static bool *guards_hit = NULL;
__attribute__((no_sanitize("coverage")))
void __sanitizer_cov_trace_pc_guard_init(uint32_t *start, uint32_t *stop) {
    if (start == stop || *start)
        return;

    total_guards = stop - start;
    guards_hit = (bool*)calloc(total_guards, sizeof(bool));
    if (!guards_hit) {
        fprintf(stderr, "Error: Failed to allocate memory for coverage tracking.\n");
        exit(1);
    }
    uint32_t counter = 1;
    for (uint32_t *x = start; x < stop; x++) {
        *x = counter++;
    }
    // printf("INIT: coverage tracking enabled for %u edges\n", total_guards);
}

__attribute__((no_sanitize("coverage")))
void __sanitizer_cov_trace_pc_guard(uint32_t *guard) {
    if (!guard || !*guard || !guards_hit)
        return;

    uint32_t index = *guard - 1;
    if (index < total_guards) {
        guards_hit[index] = true;
    }
}


__attribute__((destructor))
static void print_coverage() {
    if (!guards_hit || total_guards == 0)
        return;

    uint32_t hit = 0;
    for (uint32_t i = 0; i < total_guards; i++) {
        if (guards_hit[i])
            hit++;
    }
    double percentage = 100.0 * hit / total_guards;

    FILE *fp = fopen("/tmp/c2rust_cov.txt", "w");
    int fd = fileno(fp);

    flock(fd, LOCK_EX);
    fprintf(fp, "%.2f\n", percentage);
    fflush(fp);
    flock(fd, LOCK_UN);
    fclose(fp);
    
    free(guards_hit);
    guards_hit = NULL;
}
