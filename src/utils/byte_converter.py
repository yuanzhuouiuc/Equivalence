import numpy as np

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