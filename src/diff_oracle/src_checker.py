# from functools import lru_cache
# from multiprocessing import Pool
# import numpy as np
# import src.diff_oracle.str_handler as str_handler
# import src.diff_oracle.basic_compare as compare
# import src.data.result as res
# import src.data.constant as constant
#
# class Src_Checker:
#     def __init__(self, c_handler: str_handler.Handler, r_handler: str_handler.Handler):
#         self.c_handler = c_handler
#         self.r_handler = r_handler
#
#     def C(self, x: str):
#         self.c_handler.execute_program_subprocess(x)
#         c_result = self.c_handler.get_result()
#         c_error = self.c_handler.get_error()
#         if c_error or self.c_handler.get_exit_code() != 0:
#             return res.construct_error(c_result, c_error, self.c_handler.get_exit_code())
#         return res.detect_type(c_result.strip())
#
#     def R(self, x: str):
#         self.r_handler.execute_program_subprocess(x)
#         r_result = self.r_handler.get_result()
#         r_error = self.r_handler.get_error()
#         if r_error or self.r_handler.get_exit_code() != 0:
#             return res.construct_error(r_result, r_error, self.c_handler.get_exit_code())
#         return res.detect_type(r_result.strip())
#
#     # objective function
#     def F(self, x: str) -> float:
#         c_ret = self.C(x)
#         r_ret = self.R(x)
#         res_diff = 0.0
#         if c_ret.result_type != r_ret.result_type:
#             # found a divergence case, log it
#             compare.Compare.log_divergence(x, c_ret.original_value, r_ret.original_value, c_ret.stderr, r_ret.stderr,
#                                            constant.Constant.TYPE_MISMATCH_DIFF)
#             return -constant.Constant.TYPE_MISMATCH_DIFF
#         # handle the case by type
#         if c_ret.result_type == res.ResultType.LIST:
#             c_res = list(c_ret.parsed_value)
#             r_res = list(r_ret.parsed_value)
#             if isinstance(c_res[0], int):
#                 res_diff = compare.Compare.numba_diff_list(c_res, r_res, res.ResultType.INTEGER)
#             else:
#                 res_diff = compare.Compare.numba_diff_list(c_res, r_res, res.ResultType.STRING)
#         if c_ret.result_type in [res.ResultType.INTEGER, res.ResultType.FLOAT]:
#             c_res = float(c_ret.original_value)
#             r_res = float(r_ret.original_value)
#             res_diff += compare.Compare.diff_float(c_res, r_res)
#         if c_ret.result_type == res.ResultType.ERROR:
#             if c_ret.exit_code != r_ret.exit_code:
#                 res_diff += constant.Constant.EXIT_CODE_MISMATCH
#             # verify error pipe
#             # if not (c_ret.stderr and r_ret.stderr):
#             #     res_diff += constant.Constant.STDERR_MISMATCH
#         if res_diff > 0.0:
#             compare.Compare.log_divergence(x, c_ret.original_value, r_ret.original_value, c_ret.stderr, r_ret.stderr,
#                                            res_diff)
#         return -abs(res_diff)
#
#     @lru_cache(maxsize=1024)
#     def cached_F(self, x: str) -> float:
#         return self.F(x)
#
#     def int_step_objective(self, x: np.ndarray) -> float:
#         # transfer ndarray to string, separate by ' ' , then encode as bytes
#         x_int = np.round(x).astype(int)
#         x_str = ' '.join(map(str, x_int))  # e.g,: '1 2 3'
#         return self.cached_F(x_str)
#
#     def unicode_objective(self, x: np.ndarray) -> float:
#         char_list = [chr(int(round(code))) for code in x]
#         x_str = ' '.join(char_list)
#         return self.cached_F(x_str)
#
#     def batch_test(self, n: int, test_cases: list, exec_func):
#         with Pool(processes=6) as pool:
#             args_list = [(idx, case, n, self) for idx, case in enumerate(test_cases)]
#             results = pool.map(exec_func, args_list)
#
#         best_result = max(results, key=lambda x: x[0])
#
#         print("\nBest Result Across All Seeds:")
#         print(f"Max |C(x) - R(x)| = {best_result[0]}")
#         if best_result[0] > 0:
#             print(f"Divergence detected")
#         else:
#             print("C(x) and R(x) are equivalent for all x")
