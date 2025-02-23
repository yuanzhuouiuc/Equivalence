import math
import sys
import nlopt
import numpy as np
from numba import jit
from datetime import datetime
import src.utils.constant as constant
import src.utils.type as type

class Compare:
    @staticmethod
    def try_parse_number(s):
        """
        try to parse as float
        """
        try:
            num = float(s)
            return True, num
        except Exception:
            return False, None

    @staticmethod
    def split_elements(s):
        return s.split()

    @staticmethod
    def levenshtein_distance(s1: str, s2: str) -> int:
        """
        compute edit distance between s1, s2
        """
        m, n = len(s1), len(s2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                cost = 0 if s1[i-1] == s2[j-1] else 1
                dp[i][j] = min(dp[i-1][j] + 1,
                               dp[i][j-1] + 1,
                               dp[i-1][j-1] + cost)
        return dp[m][n]

    @staticmethod
    def objective_function(x, grad, data):
        """
        nlopt
        """
        n1 = data['n1']
        n2 = data['n2']
        diff = abs(n1 - n2)
        if diff < constant.Constant.EPSILON:
            return 1e6
        scaled_diff = abs(diff * x[0])
        target_diff = constant.Constant.DIFF_THRESHOLD + 20 * math.sqrt(diff)
        return abs(scaled_diff - target_diff)

    @staticmethod
    def optimize_scale_factor(n1, n2):
        """
        use nlopt for scale factor, to approximate the target value
        init val: 2.0, search area:[1.0, 1e6]
        """
        opt = nlopt.opt(nlopt.LN_COBYLA, 1)
        opt.set_lower_bounds([1.0])
        opt.set_upper_bounds([1e6])
        data = {'n1': n1, 'n2': n2}
        opt.set_min_objective(lambda x, grad: Compare.objective_function(x, grad, data))
        opt.set_xtol_rel(1e-9)
        opt.set_ftol_rel(1e-9)
        x = [2.0]
        try:
            opt.optimize(x)
        except Exception as e:
            return 1.0
        return x[0]

    @staticmethod
    def element_level_diff(s1, s2):
        """
        compare element
        first parse as number
        then treat as bare string
        """
        t1 = s1.strip()
        t2 = s2.strip()
        if not t1 and not t2:
            return 0.0
        is_num1, n1 = Compare.try_parse_number(t1)
        is_num2, n2 = Compare.try_parse_number(t2)
        if is_num1 and is_num2:
            diff = abs(n1 - n2)
            if diff < constant.Constant.DIFF_THRESHOLD:
                scale_factor = Compare.optimize_scale_factor(n1, n2)
                diff = abs(n1 * scale_factor - n2 * scale_factor)
            return diff
        if is_num1 != is_num2:
            return constant.Constant.TYPE_MISMATCH_DIFF
        max_len = max(len(t1), len(t2))
        if max_len == 0:
            return 0.0
        edit_dist = Compare.levenshtein_distance(t1, t2)
        return (edit_dist / max_len) * constant.Constant.STR_MISMATCH_DIFF

    @staticmethod
    def compute_diff(output1, output2):
        """
        treat as a list
        """
        if isinstance(output1, bytes):
            trimmed1 = output1.strip().decode('utf-8', errors='replace')
        else:
            trimmed1 = output1.strip()
        if isinstance(output2, bytes):
            trimmed2 = output2.strip().decode('utf-8', errors='replace')
        else:
            trimmed2 = output2.strip()
        list1 = Compare.split_elements(trimmed1)
        list2 = Compare.split_elements(trimmed2)
        if len(list1) > 1 or len(list2) > 1:
            if len(list1) != len(list2):
                return constant.Constant.LIST_LENGTH_MISMATCH_DIFF * abs(len(list1) - len(list2))
            diff = 0.0
            for elem1, elem2 in zip(list1, list2):
                diff += Compare.element_level_diff(elem1, elem2)
            return diff
        return Compare.element_level_diff(trimmed1, trimmed2)

    @staticmethod
    def diff_float(n1: float, n2: float) -> float:
        return abs(n1 - n2)

    @staticmethod
    def diff_list(list1: list, list2: list, ele_type: type.ResultType) -> float:
        # first compare the length
        if len(list1) != len(list2):
            return constant.Constant.LIST_LENGTH_MISMATCH_DIFF
        # then check the element type and compare the element
        res_diff = 0.0
        if ele_type == type.ResultType.FLOAT or ele_type == type.ResultType.INTEGER:
            for i in range(len(list1)):
                res_diff += Compare.diff_float(list1[i], list2[i])
        if ele_type == type.ResultType.STRING:
            for i in range(len(list1)):
                res_diff += Compare.levenshtein_distance(list1[i], list2[i])
        return float(res_diff)

    @staticmethod
    @jit(nopython=True)
    def diff_float_numba(list1: np.ndarray, list2: np.ndarray) -> float:
        """
        use numba for acceleration
        """
        res_diff = 0.0
        for i in range(len(list1)):
            res_diff += abs(list1[i] - list2[i])
        return res_diff

    @staticmethod
    def numba_diff_list(list1: list, list2: list, ele_type: type.ResultType) -> float:
        """
        compare lists, support inner element type int, float, string
        """
        if len(list1) != len(list2):
            return constant.Constant.LIST_LENGTH_MISMATCH_DIFF * abs(len(list1) - len(list2))

        if ele_type == type.ResultType.FLOAT or ele_type == type.ResultType.INTEGER:
            array1 = np.array(list1, dtype=np.float64)
            array2 = np.array(list2, dtype=np.float64)
            return Compare.diff_float_numba(array1, array2)

        elif ele_type == type.ResultType.STRING:
            res_diff = 0.0
            for i in range(len(list1)):
                res_diff += Compare.levenshtein_distance(list1[i], list2[i])
            return res_diff

        return 0.0

    @staticmethod
    def log_divergence(input_data, out1, out2, err1, err2, diff):
        try:
            with open("divergence.log", "ab") as logfile:
                logfile.write(b"======= DIVERGENCE DETECTED =======\n")
                logfile.write(b"[Input Data]: \n")
                if isinstance(input_data, bytes):
                    logfile.write(input_data)
                else:
                    logfile.write(input_data.encode('utf-8', errors='replace'))
                logfile.write(b"\n\n[C Program Stdout]:\n")
                if isinstance(out1, bytes):
                    logfile.write(out1)
                else:
                    logfile.write(out1.encode('utf-8', errors='replace'))
                logfile.write(b"\n\n[C Program Stderr]:\n")
                if isinstance(err1, bytes):
                    logfile.write(err1)
                else:
                    logfile.write(err1.encode('utf-8', errors='replace'))
                logfile.write(b"\n\n[Rust Program Stdout]:\n")
                if isinstance(out2, bytes):
                    logfile.write(out2)
                else:
                    logfile.write(out2.encode('utf-8', errors='replace'))
                logfile.write(b"\n\n[Rust Program Stderr]:\n")
                if isinstance(err2, bytes):
                    logfile.write(err2)
                else:
                    logfile.write(err2.encode('utf-8', errors='replace'))
                logfile.write(b"\nDifference Score: " + str(diff).encode('utf-8') + b"\n\n")
                current_time = datetime.now().strftime("%a %b %d %H:%M:%S %Y")
                logfile.write(b"\n[Time Detected]: " + current_time.encode('utf-8') + b"\n")
        except Exception as e:
            print("Error: Failed to open divergence.log for writing!", file=sys.stderr)
            return
        print("!! Found divergence case (diff={}), details logged to divergence.log".format(diff), file=sys.stderr)