import os
import sys
import threading

class capture_output:
    def __init__(self, stdout_fd=sys.stdout.fileno(), stderr_fd=sys.stderr.fileno(), chunk_size=1024):
        self._stdout_fd = stdout_fd
        self._stderr_fd = stderr_fd
        self._chunk_size = chunk_size
        self.stdout_output = b''
        self.stderr_output = b''

    def _capture(self, pipe_reader, output_attr):
        chunks = []
        while chunk := os.read(pipe_reader, self._chunk_size):
            chunks.append(chunk)
        setattr(self, output_attr, b''.join(chunks))

    def __enter__(self):
        # Save the original stdout and stderr file descriptors
        self._duped_stdout_fd = os.dup(self._stdout_fd)
        self._duped_stderr_fd = os.dup(self._stderr_fd)
        # Create pipes for stdout and stderr
        self._pipe_stdout_reader, pipe_writer = os.pipe()
        self._pipe_stderr_reader, pipe_writer_err = os.pipe()
        # Redirect stdout and stderr to the pipe
        os.dup2(pipe_writer, self._stdout_fd)
        os.dup2(pipe_writer_err, self._stderr_fd)

        os.close(pipe_writer)
        os.close(pipe_writer_err)
        # Start threads to capture stdout and stderr asynchronously
        self._capture_stdout_thread = threading.Thread(target=self._capture,
                                                       args=(self._pipe_stdout_reader, 'stdout_output'))
        self._capture_stderr_thread = threading.Thread(target=self._capture,
                                                       args=(self._pipe_stderr_reader, 'stderr_output'))
        self._capture_stdout_thread.start()
        self._capture_stderr_thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Close file descriptors and restore stdout and stderr
        os.close(self._stdout_fd)
        os.close(self._stderr_fd)
        # Wait for capture threads to finish
        self._capture_stdout_thread.join()
        self._capture_stderr_thread.join()
        os.close(self._pipe_stdout_reader)
        os.close(self._pipe_stderr_reader)
        # Restore original stdout and stderr
        os.dup2(self._duped_stdout_fd, self._stdout_fd)
        os.dup2(self._duped_stderr_fd, self._stderr_fd)
        os.close(self._duped_stdout_fd)
        os.close(self._duped_stderr_fd)


