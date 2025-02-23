import sys
import ctypes
import src.data.constant as constant
import src.algo.cma_es as ce
import src.algo.cluster_seeds as cluster
import src.diff_oracle.handler as handler
import src.diff_oracle.share_lib.c_module as c_mod
import src.diff_oracle.checker.subprocess_checker as sub_checker
import src.diff_oracle.checker.share_lib_checker as share_checker

"""
Begin the test campaign
"""
def run_subprocess(file_path: str, c_program: str, rust_program: str):
    # file_path, c_executable, rust_executable
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
    except Exception as e:
        print("Error: Failed to read from file {}: {}".format(file_path, e))
        sys.exit(1)
    buffers = content.split(b'\n')
    data, max_index = handle_buffers(buffers)
    # subprocess runner
    c_handler = handler.Handler(c_program.encode('utf-8'))
    r_handler = handler.Handler(rust_program.encode('utf-8'))
    checker = sub_checker.Sub_Checker(c_handler, r_handler)

    int_test(data, max_index, checker.int_step_objective)
    # char_test(data, max_index, checker.unicode_objective)

"""
Method for handling int type test data 
"""
def int_test(data: dict, max_index: int, obj_func: callable):
    lower_bound = constant.Constant.INT_LOWER_BOUND
    upper_bound = constant.Constant.INT_UPPER_BOUND
    # CMA_ES, handle rest
    for dim, seeds in data.items():
        if dim == max_index:
            continue
        # format convert
        seed_population = ce.convert_seeds_int_step(dim, seeds)
        cma_runner = ce.CMA_ES(dim, seed_population, obj_func, (lower_bound, upper_bound))
        cma_runner.run()

    # cluster+cma-es handle the max_index
    max_list = data[max_index]
    clu = cluster.ClusterSeeds(
        nums=max_index,
        bounds=(lower_bound, upper_bound),
        objective_function=obj_func
    )
    train_data = clu.convert_buffers_int_ndarray(max_list)
    clu.run_cluster_cma_es(train_data, True)

"""
Method for handling char type test data 
"""
def char_test(data: dict, max_index: int, obj_func: callable):
    lower_bound = constant.Constant.CHAR_LOWER_BOUND
    upper_bound = constant.Constant.CHAR_UPPER_BOUND
    # CMA_ES, handle rest
    for dim, seeds in data.items():
        if dim == max_index:
            continue
        seed_population = ce.convert_seeds_unicode_step(dim, seeds)
        cma_runner = ce.CMA_ES(dim, seed_population, obj_func, (lower_bound, upper_bound))
        cma_runner.run()

    # deap+pq, handle the max_index
    max_list = data[max_index]
    clu = cluster.ClusterSeeds(
        nums=max_index,
        bounds=(lower_bound, upper_bound),
        objective_function=obj_func
    )
    train_data = clu.convert_buffers_unicode_ndarray(max_list)
    clu.run_cluster_cma_es(train_data)

"""
function for processing input seeds generated from fuzzer
"""
def handle_buffers(buffers: list[bytes]):
    data = dict()
    max_index, max_len = -1, -1
    for buffer in buffers:
        if not buffer:
            continue
        l = len(buffer.strip().split())
        if l not in data:
            data[l] = list()
        data[l].append(buffer)
        if len(data[l]) > max_len:
            max_len = len(data[l])
            max_index = l
    return data, max_index


def run_share_lib(file_path: str, c_program: str, rust_program: str):
    # file_path, c_share_lib, c_func, rust_executable
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
    data, max_index = handle_buffers(buffers)
    r_handler = handler.Handler(rust_program.encode('utf-8'))
    checker = share_checker.Share_Checker(c_module, r_handler)

    int_test(data, max_index, checker.int_step_objective)
    # char_test(data, max_index, checker.unicode_objective)