#include "afl-help.h"
#include <unistd.h>
#include <ctype.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <sys/file.h>

#define MAX_CMDLINE_ARG_LEN 100
#define MAX_CMDLINE_LEN 100000
#define MAX_CMDLINE_PAR 1000
#define FILEPATH "./input.txt"

char **afl_init_argv(int *argc) {

    static char  in_buf[MAX_CMDLINE_LEN];
    static char *ret[MAX_CMDLINE_PAR];

    char *ptr = in_buf;
    int   rc  = 1;

    if (read(STDIN_FILENO, in_buf, MAX_CMDLINE_LEN - 2) < 0);

    while (*ptr) {

        ret[rc] = ptr;

        while (*ptr && !isspace((unsigned char)*ptr)) ptr++;
        *ptr = '\0';
        ptr++;

        while (*ptr && isspace((unsigned char)*ptr)) ptr++;

        rc++;
    }

    *argc = rc;

    return ret;
}

int write_int_array(int n, const int* numbers) {
    FILE *fp = fopen(FILEPATH, "ab");
    int fd = fileno(fp);
    flock(fd, LOCK_EX);

    char buf[32];
    for (int i = 0; i < n; i++) {
        int len = snprintf(buf, sizeof(buf), "%d", numbers[i]);
        fwrite(buf, 1, len, fp);
        if (i != n - 1) {
            fwrite(" ", 1, 1, fp);
        }
    }
    fwrite("\n", 1, 1, fp);
    flock(fd, LOCK_UN);
    fclose(fp);
    return 0;
}

int write_argv(int argc, const char *argv[]) {
    FILE *fp = fopen(FILEPATH, "ab");
    int fd = fileno(fp);
    flock(fd, LOCK_EX);

    for (int i = 1; i < argc; i++) {
        size_t len = strlen(argv[i]);
        fwrite(argv[i], 1, len, fp);
        if (i != argc - 1) {
            fwrite(" ", 1, 1, fp);
        }
    }
    fwrite("\n", 1, 1, fp);
    flock(fd, LOCK_UN);
    fclose(fp);
    return 0;
}

bool validate(void *input_data, int argc, const char *argv[], DataType type) {
    int rc  = 1;
    // based on the data type, use different strategies to cast to char*
    char *temp = NULL;
    if (input_data == NULL) return false;
    if (type == INT_TYPE) {
        int *int_data = (int *)input_data;
        // assume each integer may take up to MAX_CMDLINE_ARG_LEN bytes.
        size_t total_size = (argc - 1) * MAX_CMDLINE_ARG_LEN + 1;
        temp = (char *)malloc(total_size);
        temp[0] = '\0';  // start with an empty string

        char buffer[MAX_CMDLINE_ARG_LEN];
        for (int i = 1; i < argc; i++) {
            // Convert the i'th integer (note: int_data[i-1] corresponds to argv[i])
            // to its string representation.
            snprintf(buffer, sizeof(buffer), "%d", int_data[i - 1]);
            // Concatenate the converted string into temp.
            strcat(temp, buffer);
        }
    }
    if (type == CHAR_TYPE) {
        temp = (char *)input_data;
    }
    char *ptr = (char *)temp;
    for (int i = 1; i < argc; i++) {
        const char *arg = argv[i];
        // Skip any leading whitespace in the current argv token.
        while (*arg && isspace((unsigned char)*arg)) {
            arg++;
        }
        // Skip any whitespace in input_data.
        while (*ptr && isspace((unsigned char)*ptr)) {
            ptr++;
        }
        if (*arg == '\0')
            continue;
        // Compare the current token from argv with the next token in input_data.
        while (*arg && !isspace((unsigned char)*arg)) {
            if (*ptr != *arg) {
                // Mismatch at the binary (byte) level.
                return false;
            }
            ptr++;
            arg++;
        }
        rc++;
    }
    if (type == INT_TYPE) free(temp);
    return rc == argc;
}
