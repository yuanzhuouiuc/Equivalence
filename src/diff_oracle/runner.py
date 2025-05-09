import os
import sys
import numpy as np
import src.algo.cma_es as ce
import src.algo.mo_cma as mo_cma
import src.algo.cluster_seeds as cluster
import src.algo.proto_cma_es as proto_cma_es
import src.utils.config as config
import src.utils.constant as constant
import src.diff_oracle.handler as handler
import src.diff_oracle.parse_afl_seed as parser
import src.diff_oracle.checker.args_checker as args_checker
import src.diff_oracle.checker.stdin_checker as stdin_checker
import src.diff_oracle.protobuf.proto_driver as proto_driver

"""
Begin the test campaign, support program read input from args or stdin
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
Begin the test campaign, support program read input files
"""
def run_afl_min_seeds(seed_dir: str, c_program: str, rust_program: str):
    c_handler = handler.Handler(c_program.encode('utf-8'))
    r_handler = handler.Handler(rust_program.encode('utf-8'))
    checker = args_checker.Args_Checker(c_handler, r_handler)
    # parse the seed_dir
    data = parser.handle(seed_dir, checker)
    byte_test(data, checker.byte_step_objective)

"""
Run test for function-level fuzzing
"""
def run_proto_buf_cases(afl_queue_path: str, c_program: str, rust_program: str, proto_path: str, proto_name: str, msg_name: str):
    driver = proto_driver.ProtobufDriver(afl_queue_path, proto_path, proto_name, msg_name)
    driver.basic_check(c_program, rust_program)
    # generate population used for cma_es mutation
    afl_case_vec, min_bound_vec, max_bound_vec, case_field_infos = driver.to_vectors()
    # afl_case_vec, min_bound_vec, max_bound_vec, case_field_infos = driver.to_byte_vectors()

    c_handler = handler.Handler(c_program.encode('utf-8'))
    r_handler = handler.Handler(rust_program.encode('utf-8'))
    # use stdin for reading data by default
    checker = stdin_checker.Stdin_Checker(c_handler, r_handler)
    for i in range(len(afl_case_vec)):
        case_vec = afl_case_vec[i]
        runner = proto_cma_es.PROTO_CMA_ES(case_vec, checker.proto_buf_objective,
                        (min_bound_vec[i], max_bound_vec[i]), case_field_infos[i], driver.get_proto_handler())
        runner.run()
    return

"""
Method for handling int type test data 
"""
def int_test(data: dict, obj_func: callable):
    lower_bound = constant.Constant.INT_LOWER_BOUND
    upper_bound = constant.Constant.INT_UPPER_BOUND

    # use multi objectve cma_es
    for dim, seeds in data.items():
        if isinstance(seeds, list):
            if all(isinstance(seed, bytes) for seed in seeds):
                seeds = mo_cma.convert_seeds_int_step(dim, seeds)
        # type check
        assert isinstance(seeds, np.ndarray), "seeds should be a NumPy array"
        runner = mo_cma.MO_CMA_ES(dim, seeds, obj_func, (lower_bound, upper_bound))
        runner.run()

"""
Method for handling char type test data 
"""
def char_test(data: dict, obj_func: callable):
    lower_bound = constant.Constant.CHAR_LOWER_BOUND
    upper_bound = constant.Constant.CHAR_UPPER_BOUND

    for dim, seeds in data.items():
        if isinstance(seeds, list):
            if all(isinstance(seed, bytes) for seed in seeds):
                seeds = mo_cma.convert_seeds_unicode_step(dim, seeds)
        # type check
        assert isinstance(seeds, np.ndarray), "seeds should be a NumPy array"
        runner = mo_cma.MO_CMA_ES(dim, seeds, obj_func, (lower_bound, upper_bound))
        runner.run()

"""
Method for handling pure byte data
"""
def byte_test(data: dict, obj_func: callable):
    lower_bound = constant.Constant.BYTES_LOWER_BOUND
    upper_bound = constant.Constant.BYTES_UPPER_BOUND

    for dim, seeds in data.items():
        # type check
        assert isinstance(seeds, np.ndarray), "seeds should be a NumPy array"
        # runner = ce.CMA_ES(dim, seeds, obj_func, (lower_bound, upper_bound))
        runner = mo_cma.MO_CMA_ES(dim, seeds, obj_func, (lower_bound, upper_bound))
        runner.run()


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