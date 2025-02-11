import os
import subprocess

def read_all(fd):
    """read all data in fd (still returns bytes, since file descriptors work with bytes)"""
    blocks = []
    while True:
        chunk = os.read(fd, 4096)
        if not chunk:
            break
        blocks.append(chunk)
    return "".join([block.decode('utf-8', errors='replace') for block in blocks])

class Handler:
    def __init__(self, exec_path: str):
        self.exec_path = exec_path
        self.result = ""
        self.error = ""
        self.exit_code = -1
        self.init()

    def init(self):
        pass

    def deinit(self):
        pass

    def cleanup(self):
        """Reset the result, error, and exit_code before each execution."""
        self.result = ""
        self.error = ""
        self.exit_code = -1

    def execute_program_subprocess(self, buffer: str):
        """
        Execute the program with the given string buffer.
        :param buffer: Input string that will be passed as command-line arguments.
        """
        self.cleanup()
        args = buffer.split()  # Split the input string into arguments
        cmd = [self.exec_path] + args  # Complete command

        # Set environment variables, e.g., for AddressSanitizer (ASAN)
        env = dict(**os.environ)
        env["ASAN_OPTIONS"] = "log_to_stderr=1:abort_on_error=1:flush_on_exit=1"

        try:
            # Run the subprocess with text mode enabled to handle string input/output
            completed = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10,
                env=env,
                check=False,
                text=True,  # Ensure subprocess handles stdout/stderr as strings
                bufsize=0
            )
            self.result = completed.stdout
            self.error = completed.stderr
            self.exit_code = completed.returncode

        except subprocess.TimeoutExpired as e:
            # Handle timeout scenario
            self.result = e.stdout if e.stdout is not None else ""
            self.error = (e.stderr if e.stderr is not None else "") + "\nProcess timeout"
            self.exit_code = -1

        except Exception as e:
            # Handle general exceptions and encode the message
            self.error = str(e)
            self.exit_code = -1

    def get_result(self) -> str:
        """Return the result of the executed subprocess."""
        return self.result

    def get_error(self) -> str:
        """Return any error messages from the executed subprocess."""
        return self.error

    def get_exit_code(self) -> int:
        """Return the exit code from the executed subprocess."""
        return self.exit_code
