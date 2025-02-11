import sys
import src.diff_oracle.checker as checker
import src.diff_oracle.str_handler as str_handler
import src.algo.basin_hopping as bh
import src.algo.diff_evolution as de

def run(nums: int, file_path: str, c_program: str, rust_program: str):
    # nums, file_path, c_executable, rust_executable
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print("Error: Failed to read from file {}: {}".format(file_path, e))
        sys.exit(1)
    buffers = content.split('\n')
    c_handler = str_handler.Handler(c_program)
    r_handler = str_handler.Handler(rust_program)
    c = checker.Checker(c_handler, r_handler)

    # basin_hopping
    c.batch_test(nums, buffers, bh.Basin_Hopping.one_d_unicode_basin_hopping)
    # c.batch_test(nums, buffers, bh.Basin_Hopping.one_d_int_step_basin_hopping)

    # differential_evolution
    # de.Diff_Evolution.one_d_unicode_differential_evolution(nums, buffers, c)
    # de.Diff_Evolution.one_d_int_step_differential_evolution(nums, buffers, c)