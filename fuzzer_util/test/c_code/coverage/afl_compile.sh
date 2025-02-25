# Compile the c code with afl version
if [ -z "$1" ]; then
    echo "Usage: $0 <program_name>"
    exit 1
fi
PROGRAM_NAME="$1"
# PROGRAM_NAME="binary_search"

cp "../afl/${PROGRAM_NAME}_afl.c" .

afl-gcc-fast -fsanitize=address -o "${PROGRAM_NAME}_afl" "${PROGRAM_NAME}_afl.c"