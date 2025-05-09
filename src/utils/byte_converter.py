import numpy as np

def bytes_to_int_numpy(byte_data):
    """
    transfer bytes to uint8 numpy array
    1 int represents 1 byte
    """
    return np.frombuffer(byte_data, dtype='uint8')

def int_numpy_to_bytes(int_array):
    """
    transfer uint8 numpy array to bytes
    """
    return int_array.astype('uint8').tobytes()