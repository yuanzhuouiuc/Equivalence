/**
 * @file
 * @brief Program to perform [binary
 * search](https://en.wikipedia.org/wiki/Binary_search_algorithm) of a target
 * value in a given *sorted* array.
 * @authors [James McDermott](https://github.com/theycallmemac) - recursive
 * algorithm
 * @authors [Krishna Vedala](https://github.com/kvedala) - iterative algorithm
 */
#include <assert.h>     /// for assert
#include <stdbool.h>    /// for bool
#include <stdio.h>      /// for IO operations
#include <stdlib.h>     /// for dynammic memory allocation
#include <time.h>

/** Iterative implementation
 * \param[in] arr array to search
 * \param l left index of search range
 * \param r right index of search range
 * \param x target value to search for
 * \returns location of x assuming array arr[l..r] is present
 * \returns -1 otherwise
 */
int binarysearch2(const int *arr, int l, int r, int x) {
    while (l <= r) {
        int m = l + (r - l) / 2;

        // Check if x is present at mid
        if (arr[m] == x)
            return m;

        // If x greater, ignore left half
        if (arr[m] < x)
            l = m + 1;

            // If x is smaller, ignore right half
        else
            r = m - 1;
    }

    // if we reach here, then element was
    // not present
    return -1;
}

int n = 97;

// Read integers from command-line arguments and create an array
int *create_array_from_args(int argc, const char *argv[], int *size) {
    *size = argc - 1; // Number of integers provided as arguments

    // Allocate memory for the integers
    int *arr = (int *) malloc(*size * sizeof(int));
    if (arr == NULL) {
        printf("Memory allocation failed!\n");
        return NULL;
    }

    // Parse the command-line arguments and store them in the array
    for (int i = 0; i < *size; i++) {
        arr[i] = atoi(argv[i + 1]); // Convert argument to integer
    }

    return arr;
}

// Validating the number of arguments
void validate_arg_count(int argc, int expected_argc) {
    if (argc - 1 != expected_argc) {
        printf("Error: Expected %d arguments, but got %d.\n", expected_argc, argc - 1);
        // fprintf(stderr, "Error: Expected %d arguments, but got %d.\n", expected_argc, argc - 1);
        exit(1); // Exit the program with an error code
        //abort();
    }
}

/** Driver Code */
int main(int argc, const char *argv[]) {
    // Call the validation function to check the argument count
    validate_arg_count(argc, n);

    int *numbers = create_array_from_args(argc, argv, &n);

    volatile int k = 0;


    for (int i = 0; i < 10000; i++) {
        k = binarysearch2(numbers, 0, n, 284);
    }

    printf("%d\n", k);
    free(numbers);
    return 0;
}
