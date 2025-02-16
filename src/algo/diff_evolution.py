import numpy as np
from scipy.optimize import differential_evolution
import src.diff_oracle.subprocess_checker as sub_checker

class Diff_Evolution:
    @staticmethod
    def one_d_int_step_differential_evolution(n: int, test_cases: list, c: sub_checker.Sub_Checker):
        popsize = 25
        valid_candidates = []
        for case in test_cases:
            try:
                candidate = np.array([int(val) for val in case.strip().split()])
                if candidate.size == n:
                    valid_candidates.append(candidate)
            except Exception as e:
                print(f"Error parsing test case: {case}, error: {e}")
        bounds = [(-3147483649, 3147483648) for _ in range(n)]
        best_result = None
        best_max_difference = -np.inf
        num_runs = len(valid_candidates) // popsize
        for run in range(num_runs):
            init_population = np.empty((popsize, n))
            indices = np.random.choice(len(valid_candidates), popsize, replace=False)
            for i, idx in enumerate(indices):
                init_population[i] = valid_candidates[idx]
            result = differential_evolution(
                func=c.int_step_objective,
                bounds=bounds,
                strategy='best1bin',
                maxiter=1000,
                popsize=popsize,
                init=init_population,
                workers=6,
                polish=True
            )
            max_difference = -result.fun
            print(f"Run {run + 1}: Differential Evolution: Max |C(x) - R(x)| = {max_difference}")
            if max_difference > best_max_difference:
                best_max_difference = max_difference
                best_result = result
        print(f"Best overall result: Max |C(x) - R(x)| = {best_max_difference}")
        return best_max_difference, best_result

    @staticmethod
    def one_d_unicode_differential_evolution(n: int, test_cases: list, c: sub_checker.Sub_Checker):
        popsize = 25
        valid_candidates = []
        for case in test_cases:
            try:
                candidate = np.array([ord(char) for char in case.strip().split()], dtype=np.int32)
                if candidate.size == n:
                    valid_candidates.append(candidate)
            except Exception as e:
                print(f"Error parsing test case: {case}, error: {e}")
        bounds = [(0, 65535) for _ in range(n)]
        best_result = None
        best_max_difference = -np.inf
        num_runs = len(valid_candidates) // popsize
        for run in range(num_runs):
            init_population = np.empty((popsize, n))
            indices = np.random.choice(len(valid_candidates), popsize, replace=False)
            for i, idx in enumerate(indices):
                init_population[i] = valid_candidates[idx]
            result = differential_evolution(
                func=c.unicode_objective,
                bounds=bounds,
                strategy='best1bin',
                maxiter=30000,
                popsize=popsize,
                init=init_population,
                mutation=(0.5, 1.5),
                recombination=0.9,
                tol=0.01,
                workers=-1,
                polish=False,
                updating='immediate'
            )
            max_difference = -result.fun
            print(f"Run {run + 1}: Differential Evolution: Max |C(x) - R(x)| = {max_difference}")
            if max_difference > best_max_difference:
                best_max_difference = max_difference
                best_result = result
        print(f"Best overall result: Max |C(x) - R(x)| = {best_max_difference}")
        return best_max_difference, best_result