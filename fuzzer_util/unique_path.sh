#!/bin/bash

dir="./data/output/default/queue"
output_file="./input.txt"

touch "$output_file"

for file in "$dir"/*; do
    [ -e "$file" ] || continue
    head -n 1 "$file" >> "$output_file"
    echo "" >> "$output_file"
done

echo "Output appended to $output_file"
