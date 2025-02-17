from abc import ABC, abstractmethod
from functools import lru_cache
import numpy as np
import src.data.result as res
import src.data.constant as constant
import src.diff_oracle.basic_compare as compare

class Base_Checker(ABC):
    @abstractmethod
    def C(self, x: bytes) -> res.DetectionResult:
        pass

    @abstractmethod
    def R(self, x: bytes) -> res.DetectionResult:
        pass

    # objective function
    def F(self, x: bytes) -> float:
        c_ret = self.C(x)
        r_ret = self.R(x)
        res_diff = 0.0
        if c_ret.result_type != r_ret.result_type:
            # found a divergence case, log it
            compare.Compare.log_divergence(x, c_ret.original_value, r_ret.original_value, c_ret.stderr, r_ret.stderr,
                                           constant.Constant.TYPE_MISMATCH_DIFF)
            return -constant.Constant.TYPE_MISMATCH_DIFF
        # handle the case by type
        if c_ret.result_type == res.ResultType.LIST:
            c_res = list(c_ret.parsed_value)
            r_res = list(r_ret.parsed_value)
            if isinstance(c_res[0], int):
                res_diff = compare.Compare.numba_diff_list(c_res, r_res, res.ResultType.INTEGER)
            else:
                res_diff = compare.Compare.numba_diff_list(c_res, r_res, res.ResultType.STRING)
        if c_ret.result_type in [res.ResultType.INTEGER, res.ResultType.FLOAT]:
            c_res = float(c_ret.original_value)
            r_res = float(r_ret.original_value)
            res_diff += compare.Compare.diff_float(c_res, r_res)
        if c_ret.result_type == res.ResultType.ERROR:
            # neglect Asan Error from c_ret
            if c_ret.exit_code != r_ret.exit_code and c_ret.exit_code not in [-11, -6, 134, 139]:
                res_diff += constant.Constant.EXIT_CODE_MISMATCH
            # verify error pipe
            # if not (c_ret.stderr and r_ret.stderr):
            #     res_diff += constant.Constant.STDERR_MISMATCH
        if res_diff > 0.0:
            compare.Compare.log_divergence(x, c_ret.original_value, r_ret.original_value, c_ret.stderr, r_ret.stderr,
                                           res_diff)
        return -abs(res_diff)

    @lru_cache(maxsize=1024)
    def cached_F(self, x: bytes) -> float:
        return self.F(x)

    def int_step_objective(self, x: np.ndarray) -> float:
        # transfer ndarray to string, separate by ' ' , then encode as bytes
        x_int = np.round(x).astype(int)
        x_bytes = b' '.join(map(lambda i: str(i).encode('utf-8'), x_int))  # e.g,: b'1 2 3'
        return self.cached_F(x_bytes)

    def unicode_objective(self, x: np.ndarray) -> float:
        char_list = [chr(int(round(code))) for code in x]
        x_bytes = b' '.join(map(lambda c: c.encode('utf-8'), char_list))
        return self.cached_F(x_bytes)
