import os
import subprocess
import numpy as np
from typing import List
import src.utils.constant as constant
import src.diff_oracle.protobuf.field_info as FieldInfo
from google.protobuf.descriptor_pool import DescriptorPool
from google.protobuf.message_factory import MessageFactory
from google.protobuf.descriptor_pb2 import FileDescriptorSet
from google.protobuf.descriptor import FieldDescriptor

class ProtobufHandler:
    def __init__(self, proto_file_path: str, proto_name: str, message_type_name: str = "ProtoInput",
                 max_length: int = 128):
        """
        Initialize with a .proto file path and the main message type name.

        Args:
            proto_file_path: Path to the .proto file
            proto_name: Name of the proto file
            message_type_name: Name of the message type to handle (e.g., "ProtoInput")
            max_length: Maximum length for vector representation of string/bytes fields
        """
        self.proto_path = proto_file_path
        self.proto_name = proto_name
        self.desc_file = os.path.join(self.proto_path, f"{os.path.splitext(self.proto_name)[0]}.desc")
        self.message_type_name = message_type_name
        self.message_class = None
        self.field_names = []
        self.field_descriptors = []
        self.max_length = max_length  # Default max length for strings/bytes
        # Generate descriptor and load the message class
        self._generate_python_proto()
        self._load_message_class()

    def _generate_python_proto(self):
        """Generate the Python protocol buffer module from the .proto file."""
        # Generate descriptor set file
        subprocess.run([
            "protoc",
            f"--proto_path={self.proto_path}",
            f"--descriptor_set_out={self.desc_file}",
            "--include_imports",
            self.proto_name
        ], check=True)
        subprocess.run([
            "protoc",
            f"--proto_path={self.proto_path}",
            f"--python_out={self.proto_path}",
            self.proto_name
        ], check=True)

    def _load_message_class(self):
        """Load the message class from the descriptor."""
        # Read the descriptor file
        with open(self.desc_file, 'rb') as f:
            file_desc_set = FileDescriptorSet()
            file_desc_set.ParseFromString(f.read())
        # Create descriptor pool and add file descriptors
        desc_pool = DescriptorPool()
        for file_desc_proto in file_desc_set.file:
            desc_pool.Add(file_desc_proto)
        # Get the message descriptor and create a message factory
        message_desc = desc_pool.FindMessageTypeByName(self.message_type_name)
        factory = MessageFactory(desc_pool)
        self.message_class = factory.GetPrototype(message_desc)
        # Store field names and descriptors for vectorization
        for field in message_desc.fields:
            self.field_names.append(field.name)
            self.field_descriptors.append(field)

    def is_valid_msg(self, proto_data: bytes):
        try:
            message = self.message_class()
            message.ParseFromString(proto_data)
        except Exception:
            return False
        return True

    def is_equivalent(self, proto_data1: bytes, proto_data2: bytes):
        try:
            message1 = self.message_class()
            message2 = self.message_class()
            message1.ParseFromString(proto_data1)
            message2.ParseFromString(proto_data2)
        except Exception as e:
            print(f"Error comparing messages: {e}")
            return False
        # Compare serialized representation in bytes
        return message1.SerializeToString() == message2.SerializeToString()

    def protobuf_to_vector(self, proto_data: bytes) -> tuple[np.ndarray, np.ndarray, np.ndarray, list]:
        """
        Convert serialized protobuf data to a numerical vector.
        Returns:
            tuple: (vector, min_bounds, max_bounds, field_infos)
        """
        # Parse the raw protobuf data
        message = self.message_class()
        try:
            message.ParseFromString(proto_data)
        except Exception as e:
            raise EnvironmentError(f"Error parsing protobuf data: {e}")

        # Initialize vector parts for each field
        vector_parts = []
        min_bounds_parts = []
        max_bounds_parts = []
        vector_index = 0
        # Clear previous field info and will be used for message rebuild
        field_infos = []
        for field in self.field_descriptors:
            field_name = field.name
            field_info = FieldInfo.FieldInfo(field, vector_index)
            # Check if field is set for required fields
            if field.label == FieldDescriptor.LABEL_REQUIRED and (not message.HasField(field_name)):
                raise ValueError(f"Required field '{field_name}' is missing in the protobuf message")
            # Get field value if present
            if field.label != FieldDescriptor.LABEL_REPEATED:
                field_value = getattr(message, field_name)
                if field.type == FieldDescriptor.TYPE_MESSAGE:
                    field_vector, field_min_bounds, field_max_bounds = self._convert_message_to_vector(field_value, field_info)
                else:
                    field_vector = self._convert_field_to_vector(field, field_value)
                    field_min_bounds, field_max_bounds = self._get_field_bounds(field, len(field_vector))
            elif field.label == FieldDescriptor.LABEL_REPEATED:
                # Handle repeated fields
                field_vector = self._convert_repeated_field_to_vector(field, getattr(message, field_name), field_info)
                field_min_bounds, field_max_bounds = self._get_repeated_field_bounds(field, field_info)
            else:
                raise ValueError(f"Field '{field_name}' is missing in the protobuf message")
            field_info.set_vector_length(len(field_vector))
            field_infos.append(field_info)

            vector_parts.extend(field_vector)
            min_bounds_parts.extend(field_min_bounds)
            max_bounds_parts.extend(field_max_bounds)
            vector_index += len(field_vector)
        return np.array(vector_parts), np.array(min_bounds_parts), np.array(max_bounds_parts), field_infos

    def _convert_field_to_vector(self, field, field_value):
        """Convert a single field to a fixed-length vector representation."""
        # Handle field conversion based on type
        if field.type == FieldDescriptor.TYPE_STRING:
            return self._convert_string_to_vector(field_value)
        elif field.type == FieldDescriptor.TYPE_BYTES:
            return self._convert_bytes_to_vector(field_value)
        elif field.type == FieldDescriptor.TYPE_BOOL:
            return self._convert_bool_to_vector(field_value)
        elif field.type == FieldDescriptor.TYPE_ENUM:
            return self._convert_enum_to_vector(field_value)
        elif field.type in self._get_numeric_types():
            return self._convert_numeric_to_vector(field_value)
        else:
            raise ValueError("Unknown field type '{}'".format(field.type))

    def _convert_repeated_field_to_vector(self, field, field_values, field_info):
        """Convert a repeated field to a fixed-length vector representation."""
        vector = []
        # Track original lengths of each element
        ele_len = []
        for value in field_values:
            # first determine if inner message nested
            if field.type == FieldDescriptor.TYPE_MESSAGE:
                val_vector = self._convert_message_to_vector(value, field_info)
            else:
                val_vector = self._convert_field_to_vector(field, value)
                if len(val_vector) > self.max_length:
                    raise ValueError(f"Repeated inner element exceeds maximum length: {self.max_length}")
            ele_len.append(len(val_vector))
            vector.extend(val_vector)
        # Store the count and lengths in field_info
        field_info.set_repeated_info(len(ele_len), ele_len)
        return vector

    def _convert_string_to_vector(self, string_value):
        """Convert a string to a fixed-length vector representation."""
        # Convert to ASCII values and ensure fixed length
        vector = [ord(c) for c in string_value]
        if len(vector) > self.max_length:
            raise ValueError(f"String exceeds maximum length: {self.max_length}")
        return vector

    def _convert_bytes_to_vector(self, bytes_value):
        """Convert a bytes field to a fixed-length vector representation."""
        # Convert bytes to integers and ensure fixed length
        vector = list(bytes_value)
        if len(vector) > self.max_length:
            raise ValueError(f"Bytes exceeds maximum length: {self.max_length}")
        return vector

    def _convert_bool_to_vector(self, bool_value):
        """Convert a boolean to a fixed-length vector representation."""
        # Use 1 for True, 0 for False
        return [int(bool_value)]

    def _convert_numeric_to_vector(self, numeric_value):
        """Convert a numeric value to a fixed-length vector representation."""
        # Convert to float for uniformity and pad with zeros
        return [float(numeric_value)]

    def _convert_enum_to_vector(self, enum_value):
        """Convert an enum value to a fixed-length vector representation."""
        # Use the enum's numeric value and pad with zeros
        return [int(enum_value)]

    def _convert_message_to_vector(self, message_value, field_info):
        """
        Convert a nested message to a vector representation using recursion.

        Args:
            message_value: The protobuf message instance
            field_info: Metadata about the field's position in the vector

        Returns:
            list: Vector representation of the message
        """
        message_type_name = message_value.DESCRIPTOR.full_name
        nested_handler = ProtobufHandler(self.proto_path, self.proto_name, message_type_name, self.max_length)
        message_bytes = message_value.SerializeToString()
        # Convert to vector using the nested handler
        nested_vector, min_bounds, max_bounds, nested_field_infos = nested_handler.protobuf_to_vector(message_bytes)
        # Store the message type and handler for reconstruction
        field_info.set_message_info(message_type_name, nested_field_infos)

        return nested_vector, min_bounds, max_bounds

    def _get_numeric_types(self):
        """Return a tuple of all numeric field types."""
        return (
            FieldDescriptor.TYPE_DOUBLE,
            FieldDescriptor.TYPE_FLOAT,
            FieldDescriptor.TYPE_INT32,
            FieldDescriptor.TYPE_INT64,
            FieldDescriptor.TYPE_UINT32,
            FieldDescriptor.TYPE_UINT64,
            FieldDescriptor.TYPE_FIXED32,
            FieldDescriptor.TYPE_FIXED64,
            FieldDescriptor.TYPE_SFIXED32,
            FieldDescriptor.TYPE_SFIXED64,
            FieldDescriptor.TYPE_SINT32,
            FieldDescriptor.TYPE_SINT64
        )

    def _get_field_bounds(self, field, field_vector_length):
        """
        Get the minimum and maximum bounds for a field based on its type.
        Args:
            field: The field descriptor
            field_vector: The vector representation of the field value
        Returns:
            tuple: (min_bounds, max_bounds) lists for the field
        """
        field_type = field.type
        if field_type == FieldDescriptor.TYPE_STRING or field_type == FieldDescriptor.TYPE_BYTES:
            # String/bytes bounds: 0-255 for each character/byte
            min_bounds = [constant.Constant.CHAR_LOWER_BOUND] * field_vector_length
            max_bounds = [constant.Constant.CHAR_UPPER_BOUND] * field_vector_length
        elif field_type == FieldDescriptor.TYPE_BOOL:
            min_bounds = [0]
            max_bounds = [1]
        elif field_type == FieldDescriptor.TYPE_ENUM:
            # Get enum min and max values
            min_bounds = [constant.Constant.ENUM_LOWER_BOUND]
            max_bounds = [constant.Constant.ENUM_UPPER_BOUND]
        elif field_type in (FieldDescriptor.TYPE_INT32, FieldDescriptor.TYPE_SINT32,
                            FieldDescriptor.TYPE_SFIXED32):
            # 32-bit signed integer bounds
            min_bounds = [constant.Constant.INT_LOWER_BOUND]
            max_bounds = [constant.Constant.INT_UPPER_BOUND]
        elif field_type in (FieldDescriptor.TYPE_INT64, FieldDescriptor.TYPE_SINT64,
                            FieldDescriptor.TYPE_SFIXED64):
            min_bounds = [constant.Constant.INT64_LOWER_BOUND]
            max_bounds = [constant.Constant.INT64_UPPER_BOUND]
        elif field_type in (FieldDescriptor.TYPE_UINT32, FieldDescriptor.TYPE_FIXED32):
            # 32-bit unsigned integer bounds
            min_bounds = [constant.Constant.UINT32_LOWER_BOUND]
            max_bounds = [constant.Constant.UINT32_UPPER_BOUND]
        elif field_type in (FieldDescriptor.TYPE_UINT64, FieldDescriptor.TYPE_FIXED64):
            # 64-bit unsigned integer bounds
            min_bounds = [constant.Constant.UINT64_LOWER_BOUND]
            max_bounds = [constant.Constant.UINT64_UPPER_BOUND]
        elif field_type == FieldDescriptor.TYPE_FLOAT:
            min_bounds = [constant.Constant.FLOAT_LOWER_BOUND]
            max_bounds = [constant.Constant.FLOAT_UPPER_BOUND]
        elif field_type == FieldDescriptor.TYPE_DOUBLE:
            min_bounds = [constant.Constant.DOUBLE_LOWER_BOUND]
            max_bounds = [constant.Constant.DOUBLE_UPPER_BOUND]
        elif field_type == FieldDescriptor.TYPE_MESSAGE:
            min_bounds, max_bounds = self._get_message_bounds()
        else:
            raise ValueError(f"Unknown field type: {field_type}")
        return min_bounds, max_bounds

    def _get_repeated_field_bounds(self, field, field_info):
        """
        Get bounds for repeated fields.
        Args:
            field: The field descriptor
            field_info: Field metadata
        Returns:
            tuple: (min_bounds, max_bounds) lists for the repeated field
        """
        min_bounds = []
        max_bounds = []
        # Use the stored repeat_count and repeat_lengths
        for i in range(field_info.repeat_count):
            if field.type == FieldDescriptor.TYPE_MESSAGE:
                ele_min_bounds, ele_max_bounds = self._get_message_bounds()
            else:
                ele_min_bounds, ele_max_bounds = self._get_field_bounds(field, field_info.repeat_lengths[i])
            min_bounds.extend(ele_min_bounds)
            max_bounds.extend(ele_max_bounds)
        return min_bounds, max_bounds

    def _get_message_bounds(self):
        """
        Get bounds for message fields (placeholder implementation).
        Args:
        Returns:
            tuple: (min_bounds, max_bounds) lists for the message field
        """
        raise NotImplementedError

    def vector_to_protobuf(self, vector: np.ndarray, field_infos: list):
        """
        Convert a numerical vector back to raw bytes protobuf data.
        Args:
            vector: The numerical vector representation
            field_infos: Field metadata from protobuf_to_vector to reconstruct vector
        """
        # Create a new protobuf message
        message = self.message_class()
        # Iterate through field_infos to reconstruct each field
        for field_info in field_infos:
            field_name = field_info.name
            field_type = field_info.type
            vector_start = field_info.vector_start
            vector_length = field_info.vector_length
            # Extract the vector segment for this field
            field_vector = vector[vector_start:vector_start + vector_length]
            try:
                # Reconstruct the field based on its type and whether it's repeated
                if field_info.is_repeated:
                    self._reconstruct_repeated_field(message, field_info, field_vector)
                else:
                    # For non-repeated fields
                    if field_info.is_message:
                        self._reconstruct_message(message, field_info, field_vector)
                    else:
                        # Handle primitive types
                        self._reconstruct_primitive_field(message, field_info, field_vector)
            except Exception as e:
                print(f"Error reconstructing field {field_name}: {e}")
        # Serialize the message to bytes
        return message.SerializeToString()

    def _reconstruct_primitive_field(self, message, field_info, field_vector):
        """Reconstruct a primitive (non-message, non-repeated) field."""
        field_name = field_info.name
        field_type = field_info.type

        if field_type == FieldDescriptor.TYPE_STRING:
            # Convert vector segment to string
            chars = []
            for val in field_vector:
                if 0 <= val <= 255:
                    chars.append(chr(int(val)))
            setattr(message, field_name, ''.join(chars))

        elif field_type == FieldDescriptor.TYPE_BYTES:
            # Convert vector segment to bytes
            bytes_data = bytearray()
            for val in field_vector:
                if 0 <= val <= 255:
                    bytes_data.append(int(val))
            setattr(message, field_name, bytes(bytes_data))

        elif field_type == FieldDescriptor.TYPE_BOOL:
            # Convert to boolean
            setattr(message, field_name, bool(int(field_vector[0])))

        elif field_type == FieldDescriptor.TYPE_ENUM:
            # Convert to enum value
            setattr(message, field_name, int(field_vector[0]))

        elif field_type in self._get_numeric_types():
            # Convert to appropriate numeric type
            if field_type in (FieldDescriptor.TYPE_FLOAT, FieldDescriptor.TYPE_DOUBLE):
                setattr(message, field_name, float(field_vector[0]))
            else:
                setattr(message, field_name, int(field_vector[0]))

    def _reconstruct_repeated_field(self, message, field_info, field_vector):
        """Reconstruct a repeated field."""
        field_name = field_info.name
        field_type = field_info.type
        repeated_field = getattr(message, field_name)

        # Use the stored repeat_count and repeat_lengths to parse the vector
        offset = 0
        for i in range(field_info.repeat_count):
            length = field_info.repeat_lengths[i]
            element_vector = field_vector[offset:offset + length]

            if field_type == FieldDescriptor.TYPE_STRING:
                # Convert to string
                chars = []
                for val in element_vector:
                    if 0 <= val <= 255:
                        chars.append(chr(int(val)))
                repeated_field.append(''.join(chars))

            elif field_type == FieldDescriptor.TYPE_BYTES:
                # Convert to bytes
                bytes_data = bytearray()
                for val in element_vector:
                    if 0 <= val <= 255:
                        bytes_data.append(int(val))
                repeated_field.append(bytes(bytes_data))

            elif field_type == FieldDescriptor.TYPE_BOOL:
                # Convert to boolean
                repeated_field.append(bool(int(element_vector[0])))

            elif field_type == FieldDescriptor.TYPE_ENUM:
                # Convert to enum
                repeated_field.append(int(element_vector[0]))

            elif field_type in self._get_numeric_types():
                # Convert to numeric
                if field_type in (FieldDescriptor.TYPE_FLOAT, FieldDescriptor.TYPE_DOUBLE):
                    repeated_field.append(float(element_vector[0]))
                else:
                    repeated_field.append(int(element_vector[0]))

            elif field_type == FieldDescriptor.TYPE_MESSAGE:
                # Skip message fields for now
                # in the original code
                print(f"Skipping repeated message field {field_name} - reconstruction not implemented")
            offset += length
    #TODO
    def _reconstruct_message(self, message, field_info, field_vector):
        """
        Reconstruct a nested message from vector data using recursion.

        Args:
            message: Parent message where the reconstructed field will be set
            field_info: Field metadata including message type information
            field_vector: Vector representation of the message

        Returns:
            Reconstructed message instance
        """
        # Get the message type name
        if hasattr(field_info, 'message_type_name'):
            message_type_name = field_info.message_type_name
        else:
            # If not stored, try to get it from the field descriptor
            field_descriptor = message.DESCRIPTOR.fields_by_name[field_info.name]
            message_type_name = field_descriptor.message_type.full_name
        # Create a nested handler for this message type
        nested_handler = ProtobufHandler(self.proto_path, self.proto_name, message_type_name, self.max_length)
        # Convert the vector back to protobuf bytes
        proto_bytes = nested_handler.vector_to_protobuf(np.array(field_vector), field_info.message_filed_infos)
        # Get the field from the message
        field_name = field_info.name
        nested_message = getattr(message, field_name)
        # Parse the bytes into the message
        nested_message.ParseFromString(proto_bytes)
        return nested_message

def read_binary_file(file_path):
    with open(file_path, 'rb') as file:
        binary_data = file.read()
    return binary_data

def test():
    # proto_path = "/home/doushite/func/test/example/proto"
    # proto_name = "test.proto"
    # message_type_name = "TestInput"
    # handler = ProtobufHandler(proto_path, proto_name, message_type_name)
    # # parse file to raw bytes
    # seed_path = "/home/doushite/func/test/example/c/seeds/seed_012.bin"

    proto_path = "/home/doushite/func/test/c-strcasecmp/proto"
    proto_name = "strcasecmp_input.proto"
    message_type_name = "StrcasecmpInput"
    handler = ProtobufHandler(proto_path, proto_name, message_type_name)
    # parse file to raw bytes
    # seed_path = "/home/doushite/func/test/c-strcasecmp/c/seeds/seed_020"
    seed_path = "/home/doushite/func/test/c-strcasecmp/c/out/default/queue/id:000022,src:000001,time:152,execs:967,op:havoc,rep:2,+cov"

    from copy import deepcopy
    raw_bytes = read_binary_file(seed_path)
    copybytes = deepcopy(raw_bytes)

    vec, min_vec, max_vec, field_infos = handler.protobuf_to_vector(raw_bytes)
    ret_bytes = handler.vector_to_protobuf(vec, field_infos)

    vec2, min_vec2, max_vec2, field_infos2 = handler.protobuf_to_vector(ret_bytes)
    print(raw_bytes)
    print(ret_bytes)
    assert handler.is_equivalent(ret_bytes, copybytes) == True
    # assert ret_bytes == copybytes


if __name__ == "__main__":
    test()