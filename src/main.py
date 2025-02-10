import sys
import re
from handler import Handler
from compare import Compare, EPSILON

def main():
    # input test cases, c program, rust program
    if len(sys.argv) < 4:
        print("Error: Expected {} arguments, but got {}.".format(3, len(sys.argv) - 1))
        sys.exit(1)

    file_path = sys.argv[1]
    c_executable = sys.argv[2].encode('utf-8')
    rust_executable = sys.argv[3].encode('utf-8')
    to_utf_8(file_path)
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
    except Exception as e:
        print("Error: Failed to read from file {}: {}".format(file_path, e))
        sys.exit(1)

    # separate by '\n'
    buffers = content.split(b'\n')

    for buffer in buffers:
        buffer = buffer.strip()
        if not buffer:
            continue

        c_handler = Handler(c_executable)
        r_handler = Handler(rust_executable)

        # execute c
        c_handler.execute_program_subprocess(buffer)
        c_result = c_handler.get_result()
        c_error = c_handler.get_error()
        # c error or exit code != 0
        if c_error or c_handler.get_exit_code() != 0:
            continue
        # record successful cases
        record(buffer)
        # execute rust
        r_handler.execute_program_subprocess(buffer)
        r_result = r_handler.get_result()
        r_error = r_handler.get_error()

        diff = Compare.compute_diff(c_result, r_result)
        if diff > EPSILON:
            Compare.log_divergence(buffer, c_result, r_result, c_error, r_error, diff)

        c_handler.deinit()
        r_handler.deinit()


def to_utf_8(file_path):
    with open(file_path, "rb") as f:
        raw_data = f.read()
    decoded_text = raw_data.decode("utf-8", errors="replace")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(decoded_text)

def record(c_result):
    try:
        with open("success.txt", "ab") as file:
            file.write(c_result)
            file.write(b'\n')
    except Exception as e:
        print("Error: Failed to open success.txt for writing!", file=sys.stderr)

if __name__ == '__main__':
    main()
