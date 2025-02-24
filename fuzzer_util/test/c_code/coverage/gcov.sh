PROGRAM_NAME="binary_search"
# the file contains inputs intercepted from afl++
INPUT_FILE="../../../input.txt"

rm "*.gcno"
rm "*.gcda"
rm "*.gcov"

gcc -fsanitize=address -g -c afl-help.c -o afl-help.o
afl-gcc-fast -fsanitize=address -fprofile-arcs -ftest-coverage -g -c "${PROGRAM_NAME}_afl.c" -o "${PROGRAM_NAME}_afl.o"
afl-gcc-fast -fsanitize=address -fprofile-arcs -ftest-coverage -g -o "${PROGRAM_NAME}_afl" "${PROGRAM_NAME}_afl.o" afl-help.o

while IFS= read -r input; do
  # put current input(split by '\n') to stdin, then execute program path
  echo "$input" | AFL_FILE=stdin "./${PROGRAM_NAME}_afl"
done < "$INPUT_FILE"

gcov -b -o . "${PROGRAM_NAME}_afl.c"