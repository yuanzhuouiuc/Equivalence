#include <assert.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include "afl-help.h"

/**
 * Swap two values by using pointer
 * @param first first pointer of first number
 * @param second second pointer of second number
 */
void swap(int *first, int *second)
{
    int temp = *first;
    *first = *second;
    *second = temp;
}

/**
 * Bubble sort algorithm implementation
 * @param arr array to be sorted
 * @param size size of array
 */
void bubbleSort(int *arr, int size)
{
    for (int i = 0; i < size - 1; i++)
    {                         /* for each array index */
        /* perform iterations until no more changes were made or outer loop
            executed for all array indices */
        for (int j = 0; j < size - 1 - i; j++)
        { /* for each element in the array */
            if (arr[j] > arr[j + 1])
            { /* if the order of successive elements needs update */
                swap(&arr[j], &arr[j + 1]);
            }
        }
    }
}

int n = 97;

// Read integers from command-line arguments and create an array
int *create_array_from_args(int argc, const char *argv[], int *size) {
    *size = argc - 1;  // Number of integers provided as arguments

    // Allocate memory for the integers
    int *arr = (int *)malloc(*size * sizeof(int));
    if (arr == NULL) {
        printf("Memory allocation failed!\n");
        return NULL;
    }

    // Parse the command-line arguments and store them in the array
    for (int i = 0; i < *size; i++) {
        arr[i] = atoi(argv[i + 1]);  // Convert argument to integer
    }

    return arr;
}

// Validating the number of arguments
void validate_arg_count(int argc, int expected_argc) {
    if (argc - 1 != expected_argc) {
        printf("Error: Expected %d arguments, but got %d.\n", expected_argc, argc - 1);
        exit(1);  // Exit the program with an error code
        //abort();
    }
}

/** Driver Code */
int main(int argc, const char *argv[]) {
    AFL_INIT_ARGV();
    
    // Call the validation function to check the argument count
    validate_arg_count(argc, n);
        
    int *numbers = create_array_from_args(argc, argv, &n);
    VALIDATE_OR_EXIT(numbers, argc, argv, INT_TYPE);

/*    numbers = malloc(n * sizeof(*numbers));
    int read_count = 0;  // Counter to track successful scanf calls
    for (int i=0; i<n; i++) {
        if (scanf("%d", &numbers[i]) == 1) {
            read_count++;
        } else {
            printf("Error reading input at position %d\n", i);
            break;
        }
    }
*/    

    int size = 10000;
    //int size = 10;

    for (int i = 0; i < size; i++) {

        bubbleSort(numbers, n);

    }
    
    
    // Loop through the array and print each element
    for (int i = 0; i < n; i++) {
        printf("%d ", numbers[i]);
    }
    
    // Print a new line after the array elements
    printf("\n");
    
    free(numbers);
    WRITE_ARGV(argc, argv);
}