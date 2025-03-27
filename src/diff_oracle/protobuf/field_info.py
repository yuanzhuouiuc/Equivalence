from google.protobuf.descriptor import FieldDescriptor

class FieldInfo:
    """Class for storing field metadata during protobuf-vector conversion."""

    def __init__(self, field_descriptor, vector_start_index=0):
        """Initialize field information.
        Args:
            field_descriptor: Protocol Buffer field descriptor
            vector_start_index: Starting index of this field in the vector
        """
        self.name = field_descriptor.name
        self.type = field_descriptor.type
        self.label = field_descriptor.label
        self.vector_start = vector_start_index
        self.vector_length = 0  # Will be set during conversion
        self.is_repeated = (field_descriptor.label == FieldDescriptor.LABEL_REPEATED)
        self.is_message = (field_descriptor.type == FieldDescriptor.TYPE_MESSAGE)

        # For repeated fields
        # repeat_lengths: length for each element
        self.repeat_count = 0
        self.repeat_lengths = []
        # For message fields
        self.message_type_name = ""
        if self.is_message:
            self.message_type_name = field_descriptor.message_type.full_name
        # For repeated message fields (in repeated message fields)
        self.nested_fields = []

    def set_vector_length(self, length):
        """Set the length of the vector representation for this field."""
        self.vector_length = length

    def set_repeated_info(self, count, repeat_lengths):
        """Set information about a repeated field."""
        self.repeat_count = count
        self.repeat_lengths = repeat_lengths

    def __repr__(self):
        return (f"FieldInfo(name={self.name}, type={self.type}, label={self.label}, "
                f"vector_start={self.vector_start}, vector_length={self.vector_length})")