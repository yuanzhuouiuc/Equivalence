from enum import Enum, auto

class ResultType(Enum):
    LIST = auto()
    DICT = auto()
    TUPLE = auto()
    INTEGER = auto()
    FLOAT = auto()
    STRING = auto()
    ERROR = auto()