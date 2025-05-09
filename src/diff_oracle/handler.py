import os
import subprocess
import tempfile

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
        # Create command
        cmd = self.exec_path + b' ' + buffer
        # Create a temporary directory for execution
        with tempfile.TemporaryDirectory() as tmpdir:
            original_dir = os.getcwd()
            os.chdir(tmpdir)
            try:
                completed = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=10,
                    check=True,
                    bufsize=0,
                    shell=True
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
            finally:
                # Always return to original directory
                os.chdir(original_dir)

    def execute_program_subprocess_stdin(self, stdin_data: bytes, args_buffer: bytes = b''):
        self.cleanup()
        cmd = self.exec_path + b' ' + args_buffer
        with tempfile.TemporaryDirectory() as tmpdir:
            original_dir = os.getcwd()
            os.chdir(tmpdir)
            try:
                completed = subprocess.run(
                    cmd,
                    input=stdin_data,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=10,
                    check=False,
                    bufsize=0,
                    shell=True
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
            finally:
                os.chdir(original_dir)

    def get_result(self):
        return self.result

    def get_error(self):
        return self.error

    def get_exit_code(self):
        return self.exit_code
