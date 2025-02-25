import os
import subprocess

def read_all(fd):
    """read all data in fd"""
    blocks = []
    while True:
        chunk = os.read(fd, 4096)
        if not chunk:
            break
        blocks.append(chunk)
    return b"".join(blocks)

class Handler:
    def __init__(self, exec_path: bytes):
        self.exec_path = exec_path
        self.result = b""
        self.error = b""
        self.exit_code = -1
        self.init()

    def init(self):
        pass

    def deinit(self):
        pass

    def cleanup(self):
        self.result = b""
        self.error = b""
        self.exit_code = -1

    def execute_program_subprocess_args(self, buffer: bytes):
        self.cleanup()
        args = buffer.split()
        cmd = [self.exec_path] + args
        env = dict(**os.environ)
        env["ASAN_OPTIONS"] = "log_to_stderr=1:abort_on_error=1:flush_on_exit=1"

        try:
            completed = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10,
                env=env,
                check=False,
                bufsize=0
            )
            self.result = completed.stdout
            self.error = completed.stderr
            self.exit_code = completed.returncode
        except subprocess.TimeoutExpired as e:
            self.result = e.stdout if e.stdout is not None else b""
            self.error = (e.stderr if e.stderr is not None else b"") + b"\nProcess timeout"
            self.exit_code = -1
        except Exception as e:
            self.error = str(e).encode('utf-8', errors='replace')
            self.exit_code = -1

    def execute_program_subprocess_stdin(self, stdin_data: bytes, args_buffer: bytes = None):
        self.cleanup()
        cmd = [self.exec_path]
        if args_buffer:
            args = args_buffer.split()
            cmd += args
        env = dict(**os.environ)
        env["ASAN_OPTIONS"] = "log_to_stderr=1:abort_on_error=1:flush_on_exit=1"

        try:
            completed = subprocess.run(
                cmd,
                input=stdin_data,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10,
                env=env,
                check=False,
                bufsize=0
            )
            self.result = completed.stdout
            self.error = completed.stderr
            self.exit_code = completed.returncode
        except subprocess.TimeoutExpired as e:
            self.result = e.stdout if e.stdout is not None else b""
            self.error = (e.stderr if e.stderr is not None else b"") + b"\nProcess timeout"
            self.exit_code = -1
        except Exception as e:
            self.error = str(e).encode('utf-8', errors='replace')
            self.exit_code = -1

    def get_result(self):
        return self.result

    def get_error(self):
        return self.error

    def get_exit_code(self):
        return self.exit_code
