import numpy as np
from scipy.optimize import basinhopping
import src.data.int_step as int_step

class Basin_Hopping:
    @staticmethod
    def one_d_int_step_basin_hopping(args):
        idx, case, n, checker = args
        x0 = np.array([int(val) for val in case.strip().split()])
        if len(x0) != n:
            print(f"Test case dimension {len(x0)} does not match expected dimension {n}")
            return 0.0, None

        bounds = [(-10000, 10000) for _ in range(n)]
        integer_step = int_step.IntegerStep(stepsize=50)

        minimizer_kwargs = {"method": "L-BFGS-B", "bounds": bounds}
        result = basinhopping(checker.int_step_objective, x0, minimizer_kwargs=minimizer_kwargs, niter=300,
                              take_step=integer_step, T=1.0)
        max_difference = -result.fun
        print(f"Test case {idx + 1}: Max |C(x) - R(x)| = {max_difference}")
        return max_difference, result

    @staticmethod
    def one_d_unicode_basin_hopping(args):
        idx, case, n, checker = args
        x0 = np.array([ord(char) for char in case.strip().split()], dtype=np.int32)
        if len(x0) != n:
            print(f"Test case dimension {len(x0)} does not match expected dimension {n}")
            return 0.0, None

        bounds = [(0, 65535) for _ in range(n)]
        integer_step = int_step.IntegerStep(stepsize=1)

        minimizer_kwargs = {"method": "L-BFGS-B", "bounds": bounds}
        result = basinhopping(checker.unicode_objective, x0, minimizer_kwargs=minimizer_kwargs, niter=300,
                              take_step=integer_step, T=1.0)
        max_difference = -result.fun
        print(f"Test case {idx + 1}: Max |C(x) - R(x)| = {max_difference}")
        return max_difference, result