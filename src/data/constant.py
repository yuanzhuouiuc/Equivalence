from dataclasses import dataclass

@dataclass(frozen=True)
class Constant:
    EPSILON: float = 1e-9
    DIFF_THRESHOLD: float = 1e-4
    TYPE_MISMATCH_DIFF: float = 100.0
    STR_MISMATCH_DIFF: float = 1.0
    LIST_LENGTH_MISMATCH_DIFF: float = 10.0