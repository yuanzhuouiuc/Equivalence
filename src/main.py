import sys
import argparse
from src.diff_oracle.basic_compare import Compare
import src.diff_oracle.handler as handler
import src.diff_oracle.runner as runner
import src.utils.constant as constant
import src.utils.config as config

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
    # separate by b'\n'
    buffers = content.split(b'\n')
    for buffer in buffers:
        buffer = buffer.strip()
        if not buffer:
            continue
        c_handler = handler.Handler(c_executable)
        r_handler = handler.Handler(rust_executable)
        # execute c
        c_handler.execute_program_subprocess(buffer)
        c_result = c_handler.get_result()
        c_error = c_handler.get_error()
        # c error or exit code != 0
        if c_error or c_handler.get_exit_code() != 0:
            continue
        # execute rust
        r_handler.execute_program_subprocess(buffer)
        r_result = r_handler.get_result()
        r_error = r_handler.get_error()

        diff = Compare.compute_diff(c_result, r_result)
        if diff > constant.Constant.EPSILON:
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
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--c_executable', required=True)
    parser.add_argument('-r', '--rust_executable', required=True)
    parser.add_argument('-i', '--input_file_path', required=True)
    parser.add_argument('--checker', action='store_true')
    parser.add_argument('--gpu', action='store_true', help="Enable CUDA for clustering")
    parser.add_argument('--int', action='store_true', help="Enable when input type only contains 'int'")
    parser.add_argument('--char', action='store_true', help="Enable when input type contains 'char'")

    args = parser.parse_args()
    if args.gpu:
        config.use_gpu = True
    if args.char:
        config.char_type_data = True
    elif args.int:
        config.int_type_data = True

    if args.checker:
        runner.run_subprocess(args.input_file_path, args.c_executable, args.rust_executable)
    else:
        main()
