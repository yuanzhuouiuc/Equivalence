import sys
import ctypes
import src.diff_oracle.checker.subprocess_checker as sub_checker
import src.diff_oracle.checker.share_lib_checker as share_checker
import src.diff_oracle.share_lib.c_module as c_mod
import src.diff_oracle.handler as handler
import src.algo.cma_es as ce
import src.algo.diff_evolution as de
import src.algo.basin_hopping as bh
import src.data.constant as constant


def run_subprocess(argc: int, file_path: str, c_program: str, rust_program: str):
    # args, file_path, c_executable, rust_executable
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
    except Exception as e:
        print("Error: Failed to read from file {}: {}".format(file_path, e))
        sys.exit(1)
    buffers = content.split(b'\n')

    # subprocess runner
    c_handler = handler.Handler(c_program.encode('utf-8'))
    r_handler = handler.Handler(rust_program.encode('utf-8'))
    checker = sub_checker.Sub_Checker(c_handler, r_handler)

    # basin_hopping
    # checker.batch_test(argc, buffers, bh.Basin_Hopping.one_d_unicode_basin_hopping)
    # checker.batch_test(argc, buffers, bh.Basin_Hopping.one_d_int_step_basin_hopping)

    # differential_evolution
    # de.Diff_Evolution.one_d_unicode_differential_evolution(argc, buffers, checker)
    # de.Diff_Evolution.one_d_int_step_differential_evolution(argc, buffers, checker)

    #CMA_ES
    ce.int_step_cma_es(argc, checker, buffers)
    # ce.int_step_error_tests(argc, constant.Constant.INT_LOWER_BOUND, constant.Constant.INT_UPPER_BOUND, c)
    # ce.unicode_cma_es(argc, checker, buffers)


def run_share_lib(argc: int, file_path: str, c_program: str, rust_program: str):
    # args, file_path, c_share_lib, c_func, rust_executable
    # try to build share lib
    c_module = None
    try:
        c_module = c_mod.C_Module(
            share_lib_path=c_program,
            entry_function="main",
            argtypes=(ctypes.c_int, ctypes.POINTER(ctypes.c_char_p)),
            restype=ctypes.c_int
        )
        if not c_module:
            print("Failed to initialize the shared libraries.")
            return
        with open(file_path, 'rb') as f:
            content = f.read()
    except Exception as e:
        print(f"error: {e}")
        sys.exit(1)

    buffers = content.split(b'\n')

    r_handler = handler.Handler(rust_program.encode('utf-8'))
    checker = share_checker.Share_Checker(c_module, r_handler)

    #cma-es
    # ce.int_step_cma_es(argc, checker, buffers)
    ce.unicode_cma_es(argc, checker, buffers)
