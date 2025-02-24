# Compile the c code with afl version
if [ -z "$1" ]; then
    echo "Usage: $0 <program_name>"
    exit 1
fi
PROGRAM_NAME="$1"
# PROGRAM_NAME="binary_search"

cp "../afl/${PROGRAM_NAME}_afl.c" .

gcc -fsanitize=address -g -c afl-help.c -o afl-help.o

# afl-gcc-fast -fsanitize=address -fprofile-arcs -ftest-coverage -g -c "${PROGRAM_NAME}_afl.c" -o "${PROGRAM_NAME}_afl.o"
afl-gcc-fast -fsanitize=address -c "${PROGRAM_NAME}_afl.c" -o "${PROGRAM_NAME}_afl.o"

# afl-gcc-fast -fsanitize=address -fprofile-arcs -ftest-coverage -g -o "${PROGRAM_NAME}_afl" "${PROGRAM_NAME}_afl.o" afl-help.o
afl-gcc-fast -fsanitize=address -o "${PROGRAM_NAME}_afl" "${PROGRAM_NAME}_afl.o" afl-help.o

