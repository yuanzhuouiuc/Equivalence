import ctypes
import traceback
import multiprocessing
import src.diff_oracle.handler as handler
import src.diff_oracle.share_lib.c_module as c_mod
import src.diff_oracle.checker.base_checker as base_checker
import src.diff_oracle.checker.capture_output as capture_output
import src.data.result as res

def run_c_func(c_module: c_mod.C_Module, result_queue, *args):
    result = {
        "exit_code": None,
        "stdout": b"",
        "stderr": b"",
    }
    exit_code = 753
    try:
        with capture_output.capture_output() as captured:
            exit_code = c_module.func(*args)
    except Exception as e:
        traceback.print_exc()
    result["exit_code"] = exit_code
    result["stdout"] = captured.stdout_output
    result["stderr"] = captured.stderr_output
    result_queue.put(result)

class Share_Checker(base_checker.Base_Checker):
    def __init__(self, c_module: c_mod.C_Module, r_handler: handler.Handler):
        self.c_module = c_module
        self.r_handler = r_handler

    def C(self, x: bytes) -> res.DetectionResult:
        # create char** argv
        x_argv = tuple([b''] + list(x.split()))
        args = (ctypes.c_char_p * len(x_argv))(*x_argv)
        argc = len(x_argv)
        # execute in subprocess
        result_queue = multiprocessing.Queue()
        p = multiprocessing.Process(
            target=run_c_func,
            args=(self.c_module, result_queue, argc, args)
        )
        p.start()
        p.join()
        if p.exitcode == 0 and not result_queue.empty():
            result = result_queue.get()
            c_result = result["stdout"].decode('utf-8')
            c_error = result["stderr"].decode('utf-8')
            exit_code = int(result["exit_code"])
            if c_error or exit_code != 0:
                return res.construct_error(c_result, c_error, exit_code)
            return res.detect_type(c_result.strip())
        return res.construct_error("", "c crashed, skip this case...", p.exitcode)

    def R(self, x: bytes) -> res.DetectionResult:
        self.r_handler.execute_program_subprocess(x)
        r_result = self.r_handler.get_result().decode('utf-8')
        r_error = self.r_handler.get_error().decode('utf-8')
        if r_error or self.r_handler.get_exit_code() != 0:
            return res.construct_error(r_result, r_error, self.r_handler.get_exit_code())
        return res.detect_type(r_result.strip())
