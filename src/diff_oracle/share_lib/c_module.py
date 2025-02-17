import ctypes

class C_Module:
    def __init__(self, share_lib_path: str, entry_function: str, argtypes: ctypes._SimpleCData, restype: ctypes._SimpleCData):
        # load share lib
        self.share_lib = ctypes.CDLL(share_lib_path)
        # get target function
        self.func = getattr(self.share_lib, entry_function)
        self.func.argtypes = argtypes
        self.func.restype = restype

    def call_function(self, *args):
        return self.func(*args)
