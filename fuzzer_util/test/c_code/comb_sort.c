#include <stdio.h>
#include <stdlib.h>
#include <time.h> 
// #define SHRINK 2  // suggested shrink factor value

void sort(int numbers[], int size)
{
    int gap = size;
    float SHRINK = 2.0;
    while (gap > 1)  // gap = 1 means that the array is sorted
    {
        gap = gap / SHRINK;
        int i = 0;
        while ((i + gap) < size)
        {  // similiar to the Shell Sort
            if (numbers[i] > numbers[i + gap])
            {
                int tmp = numbers[i];
                numbers[i] = numbers[i + gap];
                numbers[i + gap] = tmp;
            }
            i++;
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
    
    // Call the validation function to check the argument count
    validate_arg_count(argc, n);
        
    int *numbers = create_array_from_args(argc, argv, &n);
    
	int size = 10000;

    for (int i = 0; i < size; i++) {

        sort(numbers, n);

    }
    
    // Loop through the array and print each element
    for (int i = 0; i < n; i++) {
        printf("%d ", numbers[i]);
    }
    
    // Print a new line after the array elements
    printf("\n");
    free(numbers);
    return 0;

}