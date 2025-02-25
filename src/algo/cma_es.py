import numpy as np
import cma
import random

class CMA_ES:
    def __init__(self, nums: int, seed_population: list[list[int]], objective_function: callable, bounds: (int, int)):
        self.nums = nums
        self._dim = nums
        self._seed_population = seed_population
        self.obj_func = objective_function
        self._lower_bound = bounds[0]
        self._upper_bound = bounds[1]

    def _objective_function(self, x):
        x_int = np.rint(x).astype(int)
        return -abs(self.obj_func(x_int))

    """
    candidates: seeds 
    num_iterations: set the generation number
    opts: params used for cma_es
    """
    def run(self, num_iterations: int = 50):
        # popsize = len(self._seed_population)
        popsize = min(2000, len(self._seed_population))
        opts = {
            'popsize': popsize,
            'CMA_mu': popsize // 2,
            'CMA_active': True,
            'bounds': [self._lower_bound, self._upper_bound],
            'maxiter': 50,  # max iter times
            'minstd': 1e-3,
            'verb_disp': 1,
            'verb_log': 0,
            'tolfun': 1e-6,
        }
        best_overall_solution = None
        best_overall_value = np.inf

        for _ in range(num_iterations):
            x0 = random.choice(self._seed_population)
            sigma = 10000
            es = cma.CMAEvolutionStrategy(x0, sigma, opts)
            NGEN = 50  # gen times
            for gen in range(NGEN):
                solutions = es.ask()
                # current strategies: hold half siblings from last generation and
                # merge the other half from initial seed population
                num_seeds = min(popsize // 10, len(self._seed_population))
                seed_indices = np.random.choice(len(self._seed_population), num_seeds, replace=False)
                for i, seed_idx in enumerate(seed_indices):
                    solutions[i] = self._seed_population[seed_idx].copy()
                if best_overall_solution is not None:
                    solutions[-1] = best_overall_solution.copy()
                fitnesses = [self._objective_function(sol) for sol in solutions]
                es.tell(solutions, fitnesses)
                es.disp()
            best_solution = np.rint(es.result.xbest).astype(int)
            best_value = es.result.fbest
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

def convert_seeds_int_step(dim: int, seeds: list[bytes]) -> list[list[int]]:
    candidates = []
    for s in seeds:
        temp = []
        s = s.decode("utf-8", errors="replace")
        for val in s.strip().split():
            try:
                i = int(val)
            except Exception as e:
                i = 0
            temp.append(i)
        candidate = np.array(temp)
        if candidate.size == dim:
            candidates.append(candidate)
    return candidates

def convert_seeds_unicode_step(dim: int, seeds: list[bytes]) -> list[list[int]]:
    candidates = []
    for s in seeds:
        if s == b'':
            continue
        temp = []
        for ch in s.strip().split():
            try:
                i = ord(ch)
            except Exception as e:
                i = 65533
            temp.append(i)
        candidate = np.array(temp)
        if candidate.size == dim:
            candidates.append(candidate)
    return candidates
