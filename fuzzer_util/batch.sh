#!/bin/bash
PROGRAM_NAME="binary_search"

#clean last fuzzing results..., the intercepted input test case will be stored at input.txt
rm input.txt
(
    cd test/c_code/coverage || { echo "Failed to cd into test/c_code/coverage"; exit 1; }
    bash clean.sh
    bash afl_compile.sh "${PROGRAM_NAME}"
)

echo "Compiling C version..."
gcc -fsanitize=address -o test/c_code/compiled/"${PROGRAM_NAME}" test/c_code/"${PROGRAM_NAME}".c

echo "Compiling Rust version..."
rustc test/rust_code/"${PROGRAM_NAME}"_safe.rs -o test/rust_code/compiled/"${PROGRAM_NAME}"_safe_rs

AFL_EXIT_WHEN_DONE=1 \
afl-fuzz \
    -i data/input_seed/"${PROGRAM_NAME}"/ \
    -o data/output/ \
    -- test/c_code/coverage/"${PROGRAM_NAME}_afl"
