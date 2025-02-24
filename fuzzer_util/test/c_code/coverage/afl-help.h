#ifndef AFL_VALIDATE_H
#define AFL_VALIDATE_H

#include <stdbool.h>

typedef enum {
    INT_TYPE,
    CHAR_TYPE
} DataType;

bool validate(void *input_data, int argc, const char *argv[], DataType type);
int write_argv(int argc, const char *argv[]);
char **afl_init_argv(int *argc);

#define AFL_INIT_ARGV()           \
do {                            \
    argv = afl_init_argv(&argc);  \
} while (0)

#define AFL_INIT_SET0(_p)            \
do {                                \
    argv = afl_init_argv(&argc);     \
    argv[0] = (_p);                  \
    if (!argc) argc = 1;             \
} while (0)

#define VALIDATE_OR_EXIT(input_data, argc, argv, type)                     \
do {                                                                   \
    if (!validate((void *) (input_data), (argc), (argv), (type))) {    \
        fprintf(stderr, "Input validation failed!\n");                 \
        free(input_data);                                              \
        exit(1);                                                       \
    }                                                                  \
} while (0)

#define WRITE_ARGV(argc, argv)    \
do {                              \
    write_argv(argc, argv);       \
} while (0)

#endif // AFL_VALIDATE_H