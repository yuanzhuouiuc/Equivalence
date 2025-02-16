import sys
import numpy as np
import src.diff_oracle.subprocess_checker as sub_checker
import src.diff_oracle.handler as handler
import src.algo.basin_hopping as bh
import src.algo.diff_evolution as de
import src.algo.cma_es as ce
import src.data.constant as constant

def run(nums: int, file_path: str, c_program: str, rust_program: str):
    # nums, file_path, c_executable, rust_executable
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print("Error: Failed to read from file {}: {}".format(file_path, e))
        sys.exit(1)
    buffers = content.split('\n')
    c_handler = handler.Handler(c_program.encode('utf-8'))
    r_handler = handler.Handler(rust_program.encode('utf-8'))
    c = sub_checker.Sub_Checker(c_handler, r_handler)

    # basin_hopping
    # c.batch_test(nums, buffers, bh.Basin_Hopping.one_d_unicode_basin_hopping)
    # c.batch_test(nums, buffers, bh.Basin_Hopping.one_d_int_step_basin_hopping)

    # differential_evolution
    # de.Diff_Evolution.one_d_unicode_differential_evolution(nums, buffers, c)
    # de.Diff_Evolution.one_d_int_step_differential_evolution(nums, buffers, c)

    #CMA_ES
    # ce.int_step_cma_es(nums, c, buffers)
    # ce.int_step_error_tests(nums, constant.Constant.INT_LOWER_BOUND, constant.Constant.INT_UPPER_BOUND, c)
    ce.unicode_cma_es(nums, c, buffers)
