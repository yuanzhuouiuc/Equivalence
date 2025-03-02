#!/bin/bash

KEEP_FILES=("afl_compile.sh" "afl-help.h" "clean.sh" "gcov.sh" "coverage_cb.c")


ALL_FILES=(*)

for file in "${ALL_FILES[@]}"; do
    if [[ ! " ${KEEP_FILES[@]} " =~ " ${file} " ]]; then
        if [[ -f "$file" ]]; then
            echo "Deleting $file"
            rm "$file"
        fi
    fi
done

echo "Cleanup complete!"
