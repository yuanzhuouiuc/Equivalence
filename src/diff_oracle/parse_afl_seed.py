import os
import numpy as np
import src.utils.byte_converter as byte_converter
import src.diff_oracle.checker.base_checker as base_checker

def handle(seed_dir: str, checker: base_checker.Base_Checker) -> dict[int, np.ndarray]:
    results = {}
    res = []
    # Iterate over each file in the provided folder
    for file_name in os.listdir(seed_dir):
        file_path = os.path.join(seed_dir, file_name)
        if os.path.isfile(file_path):
            with open(file_path, 'rb') as file:
                data = file.read()
            # try to execute the seed and filter failed one
            c_cov = checker.C(data).cov
            if c_cov == -1.0:
                continue
            res.append(data)
            np_arr = byte_converter.bytes_to_int_numpy(data)
            key = len(np_arr)
            # Group arrays by their length
            if key not in results:
                results[key] = [np_arr]
            else:
                results[key].append(np_arr)
    # Convert each list of arrays to a single NumPy array
    for key in results:
        results[key] = np.array(results[key])
    # return results
    sorted_results = dict(sorted(results.items(), key=lambda item: item[1].shape[0], reverse=True))
    s = 0

    for k, v in results.items():
        s += len(v)
    print(s)
    return sorted_results
