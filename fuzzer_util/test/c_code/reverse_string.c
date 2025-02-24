#include <string.h>
#include <assert.h>     /// for assert
#include <stdbool.h>    /// for bool
#include <stdio.h>      /// for IO operations
#include <stdlib.h>     /// for dynammic memory allocation
#include <time.h> 
// reverse string
void reverse(char s[], int length)
{
    int c;
    int i, j;

    for (i = 0, j = length - 1; i < j; i++, j--)
    {
        c = s[i];
        s[i] = s[j];
        s[j] = c;
    }
}

// reverse vector
int n = 306;

// Read integers from command-line arguments and create an array
char *create_array_from_args(int argc, const char *argv[], int *size) {
    *size = argc - 1;  // Number of integers provided as arguments

    // Allocate memory for the integers
    char *arr = (char *) malloc(*size * sizeof(char));
    if (arr == NULL) {
        printf("Memory allocation failed!\n");
        return NULL;
    }

    // Store the first character of each argument in the array
    for (int i = 0; i < *size; i++) {
        if (argv[i + 1][1] != '\0') {  // Ensure each argument is a single character
            printf("Error: Argument %d is not a single character.\n", i + 1);
            free(arr);
            return NULL;
        }
        arr[i] = argv[i + 1][0];  // Copy the first character of each argument
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
    
    // Call the validation function to check the argument count
    validate_arg_count(argc, n);
        
    char *numbers = create_array_from_args(argc, argv, &n);
    
    int size = 10000;
    for (int i = 0; i < size; i++) {

        reverse(numbers, n);

    }
    
        // Loop through the array and print each element
    for (int i = 0; i < n; i++) {
        printf("%c ", numbers[i]);
    }
    
    // Print a new line after the array elements
    printf("\n");
    free(numbers);
    return 0;

}