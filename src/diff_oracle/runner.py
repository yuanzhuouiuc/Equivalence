import sys
import numpy as np
import src.algo.cma_es as ce
import src.algo.cluster_seeds as cluster
import src.utils.config as config
import src.utils.constant as constant
import src.diff_oracle.handler as handler
import src.diff_oracle.checker.args_checker as args_checker
import src.diff_oracle.checker.stdin_checker as stdin_checker

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
    data = handle_buffers_numpy(buffers)
    # subprocess runner
    c_handler = handler.Handler(c_program.encode('utf-8'))
    r_handler = handler.Handler(rust_program.encode('utf-8'))

    checker = None
    if config.args_read:
        checker = args_checker.Args_Checker(c_handler, r_handler)
    elif config.stdin_read:
        checker = stdin_checker.Stdin_Checker(c_handler, r_handler)
    if config.char_type_data:
        char_test(data, checker.unicode_objective)
    elif config.int_type_data:
        int_test(data, checker.int_step_objective)

"""
Method for handling int type test data 
"""
def int_test(data: dict, obj_func: callable):
    lower_bound = constant.Constant.INT_LOWER_BOUND
    upper_bound = constant.Constant.INT_UPPER_BOUND

    for dim, seeds in data.items():
        # run cluster+cma-es for seeds bigger than 10000 or low dimension vector, otherwise just pure cma-es
        if len(seeds) < 10000 or dim <= 10:
            seed_population = ce.convert_seeds_int_step(dim, seeds)
            cma_runner = ce.CMA_ES(dim, seed_population, obj_func, (lower_bound, upper_bound))
            cma_runner.run(num_iterations=20)
        else:
            clu = cluster.ClusterSeeds(
                nums=dim,
                bounds=(lower_bound, upper_bound),
                objective_function=obj_func
            )
            train_data = clu.convert_buffers_int_ndarray(seeds)
            clu.run_cluster_cma_es(train_data)

"""
Method for handling char type test data 
"""
def char_test(data: dict, obj_func: callable):
    lower_bound = constant.Constant.CHAR_LOWER_BOUND
    upper_bound = constant.Constant.CHAR_UPPER_BOUND

    # deap+pq, handle the max_index
    for dim, seeds in data.items():
        if len(seeds) < 10000 or dim <= 10:
            seed_population = ce.convert_seeds_unicode_step(dim, seeds)
            cma_runner = ce.CMA_ES(dim, seed_population, obj_func, (lower_bound, upper_bound))
            cma_runner.run(num_iterations=20)
        else:
            clu = cluster.ClusterSeeds(
                nums=dim,
                bounds=(lower_bound, upper_bound),
                objective_function=obj_func
            )
            train_data = clu.convert_buffers_unicode_ndarray(seeds)
            clu.run_cluster_cma_es(train_data)


"""
function for processing input seeds generated from fuzzer
"""
def handle_buffers(buffers: list[bytes]):
    data = dict()
    for buffer in buffers:
        if not buffer:
            continue
        l = len(buffer.strip().split())
        if l not in data:
            data[l] = list()
        if buffer not in data[l]:
            data[l].append(buffer)
    return data

"""
Optimized function using NumPy to process input seeds generated from a fuzzer
"""
def handle_buffers_numpy(buffers: list[bytes]):
    buffers_np = np.array(buffers, dtype=object)
    # get rid of empty input
    buffers_np = buffers_np[buffers_np != b'']
    each_buffer_len = np.array([len(buf.strip().split()) for buf in buffers_np])
    data = {}
    unique_len = np.unique(each_buffer_len)
    for l in unique_len:
        # construct mask array for fast selection
        mask = each_buffer_len == l
        unique_seeds = np.unique(buffers_np[mask])
        data[l] = unique_seeds.tolist()
    return data