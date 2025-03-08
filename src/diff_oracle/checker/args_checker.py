import src.diff_oracle.handler as handler
import src.diff_oracle.checker.base_checker as base_checker
import src.utils.result as res

class Args_Checker(base_checker.Base_Checker):
    def __init__(self, c_handler: handler.Handler, r_handler: handler.Handler):
        self.c_handler = c_handler
        self.r_handler = r_handler

    def C(self, x: bytes) -> res.DetectionResult:
        self.c_handler.execute_program_subprocess_args(x)
        cov = base_checker._read_cov()
        c_result = self.c_handler.get_result().decode('utf-8', errors='ignore')
        c_error = self.c_handler.get_error().decode('utf-8', errors='ignore')
        if c_error or self.c_handler.get_exit_code() != 0:
            return res.construct_error(c_result, c_error, self.c_handler.get_exit_code())
        return res.parse_result(c_result.strip(), cov)

    def R(self, x: bytes) -> res.DetectionResult:
        self.r_handler.execute_program_subprocess_args(x)
        r_result = self.r_handler.get_result().decode('utf-8', errors='ignore')
        r_error = self.r_handler.get_error().decode('utf-8', errors='ignore')
        if r_error or self.r_handler.get_exit_code() != 0:
            return res.construct_error(r_result, r_error, self.r_handler.get_exit_code())
        return res.parse_result(r_result.strip())