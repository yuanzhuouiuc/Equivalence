#include <stdio.h>
#include <limits.h>
#include <stdlib.h>     /// for dynammic memory allocation
#include <time.h> 

// m is size of coins array (number of different coins) 
int minCoins(int coins[], int m, int V) 
{ 
    // table[i] will be storing the minimum number of coins 
    // required for i value.  So table[V] will have result 
    int table[V+1]; 
  
    // Base case (If given value V is 0) 
    table[0] = 0; 
  
    // Initialize all table values as Infinite 
    for (int i=1; i<=V; i++) 
        table[i] = INT_MAX; 
  
    // Compute minimum coins required for all 
    // values from 1 to V 
    for (int i=1; i<=V; i++) 
    { 
        // Go through all coins smaller than i 
        for (int j=0; j<m; j++) 
          if (coins[j] <= i) 
          { 
              int sub_res = table[i-coins[j]]; 
              if (sub_res != INT_MAX && sub_res + 1 < table[i]) 
                  table[i] = sub_res + 1; 
          } 
    }
    return table[V]; 
} 
  
// Driver program to test above function
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

    volatile int k = 0;
    int V = 98564;
 
    for (int i = 0; i < 10000; i++)
    {
        
        k = minCoins(numbers, 96, V);

    }
    printf("%d\n", k);
    free(numbers);
    return 0;
}
