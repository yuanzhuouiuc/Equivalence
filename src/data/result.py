from dataclasses import dataclass
from src.data.type import ResultType
import ast
@dataclass
class DetectionResult:
    result_type: ResultType
    original_value: str
    stderr: str
    exit_code: int
    parsed_value: object = None

def detect_type(result_str: str) -> DetectionResult:
    # parse as list, dict, tuple
    parts = result_str.split()
    if len(parts) > 1:
        if all(part.lstrip('-').isdigit() for part in parts):
            result_str = str([int(part) for part in parts])
        try:
            parsed_result = ast.literal_eval(result_str)
            if isinstance(parsed_result, list):
                return DetectionResult(ResultType.LIST, result_str, "", 0, parsed_result)
        except (ValueError, SyntaxError):
            pass
        if isinstance(parts, list):
            return DetectionResult(ResultType.LIST, result_str, "", 0, parts)
    # parse as int
    if result_str.lstrip('-').isdigit():
        return DetectionResult(ResultType.INTEGER, result_str, "", 0, int(result_str))
    # float
    try:
        return DetectionResult(ResultType.FLOAT, result_str, "", 0, float(result_str))
    except ValueError:
        pass
    # string
    return DetectionResult(ResultType.STRING, result_str, "", 0, result_str)


def construct_error(result: str, stderr: str, exit_code: int):
    return DetectionResult(ResultType.ERROR, result, stderr, exit_code, "")