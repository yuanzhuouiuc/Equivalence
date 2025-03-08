import os
import numpy as np

def handle(seed_dir: str) -> dict[int, np.ndarray]:
    results = {}
    # Iterate over each file in the provided folder
    for file_name in os.listdir(seed_dir):
        file_path = os.path.join(seed_dir, file_name)
        if os.path.isfile(file_path):
            with open(file_path, 'rb') as file:
                data = file.read()
            np_arr = bytes_to_int_numpy(data)
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

    return sorted_results


def bytes_to_int_numpy(byte_data):
    """
    transfer bytes to int numpy array(little endian, int32)
    1 int represents 4 bytes
    """
    remainder = len(byte_data) % 4
    if remainder != 0:
        padding_length = 4 - remainder
        # use ' ' to padding
        byte_data += b'\x00' * padding_length
    return np.frombuffer(byte_data, dtype='<i4')

def int_numpy_to_bytes(int_array):
    """
    transfer int numpy array(little endian, int32) to bytes
    """
    return int_array.astype('<i4').tobytes()