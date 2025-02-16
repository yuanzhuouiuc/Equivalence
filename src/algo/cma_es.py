import numpy as np
import cma
import random
import src.diff_oracle.subprocess_checker as sub_checker
import src.data.constant as constant

def clamp_solution(solution, lower_bound, upper_bound):
    return np.clip(solution, lower_bound, upper_bound)

def unicode_cma_es(nums: int, c: sub_checker.Sub_Checker, seed_population: list):
    DIMENSION = nums
    def cma_obj(x):
        x_int = np.rint(x).astype(int)
        return -c.unicode_objective(x_int)

    candidates = []
    for s in seed_population:
        try:
            candidate = np.array([int(ord(ch)) for ch in s.strip().split()])
            if candidate.size == DIMENSION:
                candidates.append(candidate)
        except Exception as e:
            print(f"parse seed error: {e}")

    popsize = 25
    best_overall_solution = None
    best_overall_value = np.inf

    for seed in candidates:
        x0 = seed.copy()  # use as init seed
        sigma = 10.0
        opts = {
            'popsize': popsize,
            'bounds': [constant.Constant.CHAR_LOWER_BOUND, constant.Constant.CHAR_UPPER_BOUND],
            'maxiter': 1000,  # max iter times
            'verb_disp': 1,
            'verb_log': 0,
        }

        es = cma.CMAEvolutionStrategy(x0, sigma, opts)
        NGEN = 100  #gen times

        for gen in range(NGEN):
            solutions = es.ask()
            if candidates:
                num_seeds = min(popsize // 2, len(candidates))
                seed_indices = np.random.choice(len(candidates), num_seeds, replace=False)
                for i, seed_idx in enumerate(seed_indices):
                    solutions[i] = candidates[seed_idx].copy()
            fitnesses = [cma_obj(sol) for sol in solutions]
            es.tell(solutions, fitnesses)
            es.disp()

        best_solution = np.rint(es.result.xbest).astype(int)
        best_value = -es.result.fbest
        print("CMA-ES best solution：")
        print(best_solution)
        print("Objective value:", best_value)
        if best_value < best_overall_value:
            best_overall_value = best_value
            best_overall_solution = best_solution
    print("overall solution:")
    print(best_overall_solution)
    print("overall objective value:", best_overall_value)
    return best_overall_solution, best_overall_value

def int_step_cma_es(nums: int, c: sub_checker.Sub_Checker, seed_population: list):
    def cma_obj(x):
        x_int = np.rint(x).astype(int)
        return c.int_step_objective(x_int)
    candidates = []
    for s in seed_population:
        try:
            candidate = np.array([int(val) for val in s.strip().split()])
            if len(candidate) == nums:
                candidates.append(candidate)
        except Exception as e:
            print(f"parse seed error: {e}")
    # population size
    popsize = 100
    best_overall_solution = None
    best_overall_value = np.inf

    for seed in candidates:
        x0 = seed.copy()  # use as init seed
        sigma = pow(10, 7)
        opts = {
            'popsize': popsize,
            'CMA_mu': popsize // 2,
            'CMA_active': True,
            'bounds': [constant.Constant.INT_LOWER_BOUND, constant.Constant.INT_UPPER_BOUND],
            'maxiter': 500,  # max iter times
            'verb_disp': 1,
            'verb_log': 0,
            'tolfun': 1e-8,
        }
        es = cma.CMAEvolutionStrategy(x0, sigma, opts)
        NGEN = 1000  #gen times

        for gen in range(NGEN):
            solutions = es.ask()
            if candidates:
                num_seeds = min(popsize // 2, len(candidates))
                seed_indices = np.random.choice(len(candidates), num_seeds, replace=False)
                for i, seed_idx in enumerate(seed_indices):
                    solutions[i] = candidates[seed_idx].copy()
            fitnesses = [cma_obj(sol) for sol in solutions]
            es.tell(solutions, fitnesses)
            es.disp()

        best_solution = np.rint(es.result.xbest).astype(int)
        best_value = -es.result.fbest
        print("CMA-ES best solution：")
        print(best_solution)
        print("Objective value:", best_value)
        if best_value < best_overall_value:
            best_overall_value = best_value
            best_overall_solution = best_solution

    print("overall solution:")
    print(best_overall_solution)
    print("overall objective value:", best_overall_value)
    return best_overall_solution, best_overall_value


def int_step_error_tests(nums: int, lower_bound: int, upper_bound: int, c: sub_checker.Sub_Checker):
    for i in range(nums - 1, nums + 2):  # Ensure you generate 2*nums arrays
        # Generate a list of i random integers between lower_bound and upper_bound
        arr = [str(random.randint(lower_bound, upper_bound)) for _ in range(i)]
        # Join the list of integers into a string with spaces
        arr_str = " ".join(arr)
        # Call int_step_cma_es with the generated string
        int_step_cma_es(i, c, [arr_str])