from dataclasses import dataclass

@dataclass(frozen=True)
class Constant:
    EPSILON: float = 1e-9
    DIFF_THRESHOLD: float = 1e-4
    TYPE_MISMATCH_DIFF: float = 100.0
    STR_MISMATCH_DIFF: float = 1.0
    LIST_LENGTH_MISMATCH_DIFF: float = 10.0
    EXIT_CODE_MISMATCH = 20.0
    STDERR_MISMATCH = 20.0
    INT_LOWER_BOUND = -2147483648
    INT_UPPER_BOUND = 2147483647
    CHAR_LOWER_BOUND = 0
    CHAR_UPPER_BOUND = 65535