# #!/usr/bin/env python3
# import math
# import sys
# import nlopt
#
# # 下面这些常量的取值可根据实际需要调整
# EPSILON = 1e-9
# DIFF_THRESHOLD = 1e-4
# TYPE_MISMATCH_DIFF = 1000.0
# STR_MISMATCH_DIFF = 1.0
# LIST_LENGTH_MISMATCH_DIFF = 10.0
#
#
# class Compare:
#     @staticmethod
#     def try_parse_number(s):
#         """
#         尝试将字符串 s 转换为浮点数。
#         如果能完全解析，则返回 (True, number)；否则返回 (False, None)
#         """
#         try:
#             num = float(s)
#             return True, num
#         except ValueError:
#             return False, None
#
#     @staticmethod
#     def split_elements(s):
#         """
#         根据空白字符分割字符串，返回元素列表
#         """
#         return s.split()
#
#     @staticmethod
#     def levenshtein_distance(s1, s2):
#         """
#         计算字符串 s1 与 s2 之间的 Levenshtein 编辑距离
#         """
#         m, n = len(s1), len(s2)
#         # 构造 (m+1) x (n+1) 的二维数组
#         dp = [[0] * (n + 1) for _ in range(m + 1)]
#         for i in range(m + 1):
#             dp[i][0] = i
#         for j in range(n + 1):
#             dp[0][j] = j
#
#         for i in range(1, m + 1):
#             for j in range(1, n + 1):
#                 cost = 0 if s1[i - 1] == s2[j - 1] else 1
#                 dp[i][j] = min(dp[i - 1][j] + 1,      # 删除
#                                dp[i][j - 1] + 1,      # 插入
#                                dp[i - 1][j - 1] + cost)  # 替换
#         return dp[m][n]
#
#     @staticmethod
#     def objective_function(x, grad, data):
#         """
#         nlopt 的目标函数：
#         data 为字典，包含 'n1' 与 'n2' 两个数值；
#         目标：寻找一个放缩因子，使得 |n1 - n2| 经过放缩后能“放大”到
#         DIFF_THRESHOLD + 20 * sqrt(|n1 - n2|) 附近。
#         如果 n1 与 n2 差异过小，则返回一个较大的目标值 1e6，以避免无意义的优化。
#         """
#         n1 = data['n1']
#         n2 = data['n2']
#         diff = abs(n1 - n2)
#         if diff < EPSILON:
#             return 1e6
#         scaled_diff = abs(diff * x[0])
#         target_diff = DIFF_THRESHOLD + 20 * math.sqrt(diff)
#         return abs(scaled_diff - target_diff)
#
#     @staticmethod
#     def optimize_scale_factor(n1, n2):
#         """
#         通过 nlopt 求解最合适的放缩因子（scaler），以使得经过放缩后两数的差异达到目标值。
#         初始猜测为 2.0，允许的范围为 [1.0, 1e6]。
#         """
#         opt = nlopt.opt(nlopt.LN_COBYLA, 1)
#         opt.set_lower_bounds([1.0])
#         opt.set_upper_bounds([1e6])
#         data = {'n1': n1, 'n2': n2}
#         opt.set_min_objective(lambda x, grad: Compare.objective_function(x, grad, data))
#         opt.set_xtol_rel(1e-9)
#         opt.set_ftol_rel(1e-9)
#         x = [2.0]
#         try:
#             # nlopt.optimize 会修改 x
#             opt.optimize(x)
#         except Exception as e:
#             # 若优化失败，返回默认因子 1.0
#             return 1.0
#         return x[0]
#
#     @staticmethod
#     def element_level_diff(s1, s2):
#         """
#         对两个单独元素（字符串）进行比较：
#           - 如果二者都能解析成数字，则计算两数之差，若差值较小则尝试放大；
#           - 如果一个能解析成数字而另一个不能，则返回一个较大差异值；
#           - 否则，采用 Levenshtein 距离归一化后的结果作为差异值。
#         """
#         t1 = s1.strip()
#         t2 = s2.strip()
#         if not t1 and not t2:
#             return 0.0
#
#         is_num1, n1 = Compare.try_parse_number(t1)
#         is_num2, n2 = Compare.try_parse_number(t2)
#         if is_num1 and is_num2:
#             diff = abs(n1 - n2)
#             # 如果数值差异太小，尝试用放缩因子“放大”差异
#             if diff < DIFF_THRESHOLD:
#                 scale_factor = Compare.optimize_scale_factor(n1, n2)
#                 diff = abs(n1 * scale_factor - n2 * scale_factor)
#             return diff
#         # 数值类型不匹配
#         if is_num1 != is_num2:
#             return TYPE_MISMATCH_DIFF
#
#         # 如果不能解析为数字，则按字符串比较：采用归一化的 Levenshtein 编辑距离
#         max_len = max(len(t1), len(t2))
#         if max_len == 0:
#             return 0.0
#         edit_dist = Compare.levenshtein_distance(t1, t2)
#         d = (edit_dist / max_len) * STR_MISMATCH_DIFF
#         return d
#
#     @staticmethod
#     def compute_diff(output1, output2):
#         """
#         对两个输出进行比较：
#           1. 先去除首尾空白；
#           2. 尝试将输出拆分成多个元素（按空白拆分）；
#           3. 如果拆分后元素个数大于 1，则逐元素比较；否则直接比较整个字符串。
#         """
#         trimmed1 = output1.strip()
#         trimmed2 = output2.strip()
#         list1 = Compare.split_elements(trimmed1)
#         list2 = Compare.split_elements(trimmed2)
#
#         if len(list1) > 1 or len(list2) > 1:
#             # 如果拆分后列表长度不同，则直接按长度差返回一个较大值
#             if len(list1) != len(list2):
#                 return LIST_LENGTH_MISMATCH_DIFF * abs(len(list1) - len(list2))
#             diff = 0.0
#             for elem1, elem2 in zip(list1, list2):
#                 diff += Compare.element_level_diff(elem1, elem2)
#             return diff
#
#         # 非列表情况直接比较整个字符串
#         return Compare.element_level_diff(trimmed1, trimmed2)
#
#     @staticmethod
#     def log_divergence(input_data, out1, out2, err1, err2, diff):
#         """
#         当比较结果显示两份输出存在较大差异时，
#         将原始输入、C 与 Rust 程序的输出和错误信息以及差异值记录到文件 divergence.log 中，
#         同时在标准错误输出提示信息。
#         """
#         try:
#             # 以二进制追加方式打开日志文件
#             with open("divergence.log", "ab") as logfile:
#                 logfile.write(b"======= DIVERGENCE DETECTED =======\n")
#                 logfile.write(b"[Input Data]: \n")
#                 logfile.write(input_data.encode("utf-8"))
#                 logfile.write(b"\n\n[C Program Stdout]:\n")
#                 logfile.write(out1.encode("utf-8"))
#                 logfile.write(b"\n\n[C Program Stderr]:\n")
#                 logfile.write(err1.encode("utf-8"))
#                 logfile.write(b"\n\n[Rust Program Stdout]:\n")
#                 logfile.write(out2.encode("utf-8"))
#                 logfile.write(b"\n\n[Rust Program Stderr]:\n")
#                 logfile.write(err2.encode("utf-8"))
#                 logfile.write(b"\nDifference Score: " + str(diff).encode("utf-8") + b"\n\n")
#         except Exception as e:
#             print("Error: Failed to open divergence.log for writing!", file=sys.stderr)
#             return
#
#         print("!! Found divergence case (diff={}), details logged to divergence.log".format(diff), file=sys.stderr)
#!/usr/bin/env python3
import math
import sys
import nlopt

# 常量设置（可根据实际需要调整）
EPSILON = 1e-9
DIFF_THRESHOLD = 1e-4
TYPE_MISMATCH_DIFF = 1000.0
STR_MISMATCH_DIFF = 1.0
LIST_LENGTH_MISMATCH_DIFF = 10.0

class Compare:
    @staticmethod
    def try_parse_number(s):
        """
        尝试将字符串 s 转换为浮点数。
        s 期望为 str（因此在外层调用前请先 decode）。
        返回 (True, number) 或 (False, None)
        """
        try:
            num = float(s)
            return True, num
        except Exception:
            return False, None

    @staticmethod
    def split_elements(s):
        """
        按空白字符拆分字符串，s 期望为 str。
        """
        return s.split()

    @staticmethod
    def levenshtein_distance(s1, s2):
        """
        计算 s1 与 s2 之间的 Levenshtein 编辑距离（s1、s2 均为 str）。
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
                dp[i][j] = min(dp[i-1][j] + 1,      # 删除
                               dp[i][j-1] + 1,      # 插入
                               dp[i-1][j-1] + cost) # 替换
        return dp[m][n]

    @staticmethod
    def objective_function(x, grad, data):
        """
        nlopt 目标函数。
        data 为包含 'n1' 和 'n2' 的字典。
        """
        n1 = data['n1']
        n2 = data['n2']
        diff = abs(n1 - n2)
        if diff < EPSILON:
            return 1e6
        scaled_diff = abs(diff * x[0])
        target_diff = DIFF_THRESHOLD + 20 * math.sqrt(diff)
        return abs(scaled_diff - target_diff)

    @staticmethod
    def optimize_scale_factor(n1, n2):
        """
        利用 nlopt 优化求解合适的放缩因子，使得放缩后两数之差接近目标值。
        初始猜测为 2.0，搜索区间为 [1.0, 1e6]。
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
        对两个单独元素进行比较（s1 和 s2 均为 str）：
          - 若两者均能解析为数字，则比较数值差异（不足 DIFF_THRESHOLD 时尝试放大）；
          - 若一者为数字另一者不是，则返回 TYPE_MISMATCH_DIFF；
          - 否则采用归一化的 Levenshtein 编辑距离。
        """
        t1 = s1.strip()
        t2 = s2.strip()
        if not t1 and not t2:
            return 0.0
        is_num1, n1 = Compare.try_parse_number(t1)
        is_num2, n2 = Compare.try_parse_number(t2)
        if is_num1 and is_num2:
            diff = abs(n1 - n2)
            if diff < DIFF_THRESHOLD:
                scale_factor = Compare.optimize_scale_factor(n1, n2)
                diff = abs(n1 * scale_factor - n2 * scale_factor)
            return diff
        if is_num1 != is_num2:
            return TYPE_MISMATCH_DIFF
        max_len = max(len(t1), len(t2))
        if max_len == 0:
            return 0.0
        edit_dist = Compare.levenshtein_distance(t1, t2)
        return (edit_dist / max_len) * STR_MISMATCH_DIFF

    @staticmethod
    def compute_diff(output1, output2):
        """
        比较两个输出（output1 与 output2）。
        如果参数为 bytes，则先解码为 UTF-8（错误部分用替换字符）。
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
                return LIST_LENGTH_MISMATCH_DIFF * abs(len(list1) - len(list2))
            diff = 0.0
            for elem1, elem2 in zip(list1, list2):
                diff += Compare.element_level_diff(elem1, elem2)
            return diff
        return Compare.element_level_diff(trimmed1, trimmed2)

    @staticmethod
    def log_divergence(input_data, out1, out2, err1, err2, diff):
        """
        当发现较大差异时，将原始输入、两个程序的输出及错误信息和差异值记录到日志文件。
        参数可为 bytes 或 str；如果为 str，则转换为 UTF-8 编码写入。
        """
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
        except Exception as e:
            print("Error: Failed to open divergence.log for writing!", file=sys.stderr)
            return
        print("!! Found divergence case (diff={}), details logged to divergence.log".format(diff), file=sys.stderr)
