import os
import numpy as np
import src.diff_oracle.handler as handler
from src.diff_oracle.basic_compare import Compare
import src.diff_oracle.protobuf.proto_buf as proto_buf

class ProtobufDriver():
    def __init__(self, afl_queue_path: str, proto_path: str, proto_name: str, msg_name: str):
        self._afl_queue_path = afl_queue_path
        self._proto_path = proto_path
        self._proto_name = proto_name
        self._msg_name = msg_name
        # generate protobuf handler
        self._proto_handler = proto_buf.ProtobufHandler(self._proto_path, self._proto_name, self._msg_name)

    """
    Function for converting afl++ queue cases to vectors for mutation, and bounds vectors
    """
    def to_vectors(self) -> tuple[list, list, list, list]:
        afl_cases = self._process(self._afl_queue_path)
        vectors = []
        min_bound_vectors = []
        max_bound_vectors = []
        vec_field_infos = []
        for case in afl_cases:
            try:
                if not self._proto_handler.is_valid_msg(case):
                    continue
                vec, min_bound_vec, max_bound_vec, field_infos = self._proto_handler.protobuf_to_vector(case)
            except Exception as e:
                print(f"Error parsing protobuf data: {e}")
                continue
            # verify translation robustness
            trans_case = self._proto_handler.vector_to_protobuf(vec, field_infos)
            # if not self._proto_handler.is_equivalent(case, trans_case):
            #     print(f"Not equivalent case when parsing protobuf data to vectors: {vec}!!!!!!!")
            #     continue
            trans_vec = self._proto_handler.protobuf_to_vector(trans_case)[0]
            assert (trans_vec == vec).all()
            # generate bound vector for this case
            vectors.append(vec)
            min_bound_vectors.append(min_bound_vec)
            max_bound_vectors.append(max_bound_vec)
            vec_field_infos.append(field_infos)
        return vectors, min_bound_vectors, max_bound_vectors, vec_field_infos

    """
    Function for converting afl++ queue cases to vectors for mutation, but without protobuf driver
    Only convert bytes strings to int arrays, each uint8 stands for a byte data
    """
    def to_byte_vectors(self) -> tuple[list, list, list, list]:
        afl_cases = self._process(self._afl_queue_path)
        vectors = []
        min_bound_vectors = []
        max_bound_vectors = []
        vec_field_infos = []
        for case in afl_cases:
            try:
                if not self._proto_handler.is_valid_msg(case):
                    continue
                vec = np.frombuffer(case, dtype='uint8')
                min_bound_vec = np.zeros(len(vec), dtype='uint8')
                max_bound_vec = np.full(len(vec), 255, dtype='uint8')
                field_infos = None
            except Exception as e:
                print(f"Error parsing protobuf data: {e}")
                continue
            # generate bound vector for this case
            vectors.append(vec)
            min_bound_vectors.append(min_bound_vec)
            max_bound_vectors.append(max_bound_vec)
            vec_field_infos.append(field_infos)
        return vectors, min_bound_vectors, max_bound_vectors, vec_field_infos

    """
    Function for checking if afl++ queue can trigger divergence case
    """
    def basic_check(self, c_executable: str, rust_executable: str):
        afl_cases = self._process(self._afl_queue_path)
        c_handler = handler.Handler(c_executable.encode('utf-8'))
        r_handler = handler.Handler(rust_executable.encode('utf-8'))
        for case in afl_cases:
            # execute c
            c_handler.execute_program_subprocess_stdin(case)
            c_result = c_handler.get_result()
            c_error = c_handler.get_error()
            # c error exists or exit code != 0
            if c_error or c_handler.get_exit_code() != 0:
                continue
            # execute rust
            r_handler.execute_program_subprocess_stdin(case)
            r_result = r_handler.get_result()
            r_error = r_handler.get_error()
            diff = Compare.compute_diff(c_result, r_result)
            if diff != 0:
                Compare.log_divergence(case, c_result, r_result, c_error, r_error, diff)

    def get_proto_handler(self):
        return self._proto_handler

    def _process(self, folder_path: str) -> list[bytes]:
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            print(f"Error: The path '{folder_path}' does not exist or is not a directory.")
            return []
        all_files = []
        # List only files in the top directory
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if os.path.isfile(item_path):
                data = self._read_binary_file(item_path)
                all_files.append(data)
        return all_files

    def _read_binary_file(self, file_path: str) -> bytes:
        with open(file_path, 'rb') as file:
            binary_data = file.read()
        return binary_data