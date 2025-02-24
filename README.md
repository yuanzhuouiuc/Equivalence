# Equivalence

## Usage
fuzzer_util folder contains some example source code for fuzzer testing, which is not important actually. You can also put your testcases wherever you like, as long as they stick to the AFL++ rules.

The only important code resides in fuzzer_util/test/c_code/coverage folder.

## How to use fuzzer_util
In fuzzer_util/test/c_code/coverage folder, afl-help.c&h files were used to do some functional checking and AFL testcases interception.
### AFL_INIT_ARGV();
This micro was provided by AFL official, which was used to support afl fuzzing for programs read inputs from command line arguments.
Deatailed can be found here:
https://github.com/AFLplusplus/AFLplusplus/tree/stable/utils/argv_fuzzing
### VALIDATE_OR_EXIT(parsed_data, argc, argv, TYPE);
This micro was used for input equivalence checking, to block the input testcases which are not equivalent with the origianl input data.
### WRITE_ARGV(argc, argv);
This micro was used to record the testcase successfully executed the whole c program.And each case will be in a standalone line in the output file.

### Example usage:
```
int main(int argc, const char *argv[]) {
    AFL_INIT_ARGV();
    // Call the validation function to check the argument count
    validate_arg_count(argc, n);

    int *numbers = create_array_from_args(argc, argv, &n);
    VALIDATE_OR_EXIT(numbers, argc, argv, INT_TYPE);

    volatile int k = 0;


    for (int i = 0; i < 10000; i++)

    {

        k = binarysearch2(numbers, 0, n, 284);

    }

    printf("%d\n", k);
    free(numbers);
    WRITE_ARGV(argc, argv);
    return 0;
}
```
Please include `AFL_INIT_ARGV();` in the first line of the main(entry) function.

`VALIDATE_OR_EXIT(parsed_data, argc, argv, TYPE);` has 4 params, just put it after the c program has handled the input handling(in this case: `int *numbers = create_array_from_args(argc, argv, &n);` handled the input data and create the array, so we just put the array as 'parsed_data'). 'argc&argv' just stays the same with the main function arguments. TYPE now only support two types:'INT_TYPE' and 'CHAR_TYPE', if the input only contains 'int' type data, please use 'INT_TYPE', for 'char *' type data please use 'CHAR_TYPE'.

Then, just put `WRITE_ARGV(argc, argv);` before the program returns successfully.

Fianlly, put `#include "afl-help.h"` in your source code for AFL++ testing.

### Compile Method
```
gcc -fsanitize=address -g -c afl-help.c -o afl-help.o
afl-gcc-fast -fsanitize=address -c test_program.c -o test_program.o
afl-gcc-fast -fsanitize=address -o test_program test_program.o afl-help.o
```
Then use AFL++ for fuzzing
```
AFL_EXIT_WHEN_DONE=1 \
afl-fuzz \
    -i input_seed_folder/ \
    -o afl_output_folder \
    -- test_program
```

### fuzzer_util output
Ideally, the fuzzing will generate 'input.txt' which contains testcases intercepted from AFL++, which passed the input equivalence checking and returned successfully. Each case is stored in a single line.
## src folder
This contains the oracle for differential testing.

### Usage command line
data which is 'int' type:
```
python3 src/main.py --checker --int -c c_executable -r rust_executable -i input_file_path
```
data which is 'char *' type:
```
python3 src/main.py --checker --char -c c_executable -r rust_executable -i input_file_path
```

'c_executable' stands for gcc compiled executable path of the c code you want to test.

'rust_executable' stands for rustc compiled executable path of the rust code you want to test.

'input_file_path' is the output file(intercepted testcases. 'input.txt') generated from AFL++ testing.
### For Cuda Acceleration
Add '--gpu' in the usage cmd

Installation: Reference to RapidsAi for installation
https://docs.rapids.ai/install/

Example install command:

conda create -n rapids-23.12 -c rapidsai -c nvidia -c conda-forge rapids=23.12 python=3.10 cudatoolkit=11.8