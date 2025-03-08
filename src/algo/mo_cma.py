import numpy as np
import random
from deap import base, creator, tools
from deap.cma import StrategyMultiObjective


class MO_CMA_ES:

    def __init__(self, dim: int, seed_population: np.array, objective_function: callable, bounds: (np.array, np.array)):
        """
        :param dim: vector dimension
        :param seed_population: initial population, shape: (n, dim)
        :param objective_function: objective function, return diff, code coverage
        """
        self._dim = dim
        self._seed_population = seed_population
        self._obj_func = objective_function
        self._lower_bound = bounds[0]
        self._upper_bound = bounds[1]
        self._lambda = min(200, len(self._seed_population))
        self._mu = self._lambda // 2

    def _evaluate(self, x):
        x_int = np.rint(x).astype(int)
        diff, c_cov = self._obj_func(x_int)
        return (abs(diff), c_cov)

    def _validity(self, ind):
        arr = np.array(ind)
        return np.all(arr >= self._lower_bound) and np.all(arr <= self._upper_bound)

    def _feasible(self, ind):
        arr = np.array(ind)
        arr = np.maximum(self._lower_bound, arr)
        arr = np.minimum(self._upper_bound, arr)
        return arr.tolist()

    def _distance(self, feasible_ind, original_ind):
        return sum((f - o) ** 2 for f, o in zip(feasible_ind, original_ind))

    def _setup(self):
        creator.create("FitnessMulti", base.Fitness, weights=(1.0, 0.1))
        creator.create("Individual", list, fitness=creator.FitnessMulti)

        toolbox = base.Toolbox()
        toolbox.register("evaluate", self._evaluate)
        # toolbox.decorate("evaluate", tools.ClosestValidPenalty(self._validity, self._feasible, 1.0e+6, self._distance))

        pop = self._init_pop()
        for ind in pop:
            ind.fitness.values = toolbox.evaluate(ind)
        strategy = StrategyMultiObjective(pop, sigma=10000, lambda_=self._lambda, mu=self._mu)
        toolbox.register("generate", strategy.generate, creator.Individual)
        toolbox.register("update", strategy.update)

        stats = tools.Statistics(lambda x: x.fitness.values)
        stats.register("min", np.min, axis=0)
        stats.register("max", np.max, axis=0)

        logbook = tools.Logbook()
        logbook.header = ["gen", "nevals"] + (stats.fields if stats else [])
        hof = tools.HallOfFame(1)
        return toolbox, strategy, stats, logbook, hof

    def _init_pop(self):
        num_seeds = min(self._lambda, len(self._seed_population))
        pop = [None] * num_seeds
        seed_indices = np.random.choice(len(self._seed_population), num_seeds, replace=False)
        for i, seed_idx in enumerate(seed_indices):
            seed = self._seed_population[seed_idx].astype(float)
            pop[i] = creator.Individual(seed.tolist())
        return pop

    def _diverse(self, population):
        num_seeds = self._lambda // 4
        seed_indices = np.random.choice(len(self._seed_population), num_seeds, replace=False)
        for i, seed_idx in enumerate(seed_indices):
            population[i][:] = creator.Individual(self._seed_population[seed_idx].tolist())

    def run(self, NGEN: int = 150):
        toolbox, strategy, stats, logbook, hof = self._setup()
        stag_cnt, stag_limit = 0, 10
        best_fitness = 0.0
        overall_best_fitness = 0.0

        for gen in range(NGEN):
            population = toolbox.generate()
            if best_fitness != 0.0:
                self._diverse(population)
            # have found divergence case, now we need to diverse population to avoid local minimum
            if stag_cnt >= stag_limit:
                print(f"Restarting CMA-ES at generation {gen} due to stagnation.")
                toolbox, strategy, stats, logbook, hof = self._setup()
                stag_cnt = 0
                best_fitness = 0.0
                continue
            fitness = toolbox.map(toolbox.evaluate, population)
            for ind, fit in zip(population, fitness):
                ind.fitness.values = fit
            toolbox.update(population)
            hof.update(population)

            cur_best_diff = hof[0].fitness.values[0]
            if cur_best_diff > best_fitness:
                best_fitness = cur_best_diff
                stag_cnt = 0
            elif cur_best_diff == best_fitness and best_fitness != 0.0:
                stag_cnt += 1
            overall_best_fitness = max(overall_best_fitness, best_fitness)
            record = stats.compile(population) if stats is not None else {}
            logbook.record(gen=gen, nevals=len(population), **record)
            print(logbook.stream)
        # print("\nBest individual found:", hof[0])
        # print("Best fitness:", hof[0].fitness.values)
        return

def convert_seeds_int_step(dim: int, seeds: list[bytes]) -> np.array:
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
        candidate = np.array(temp, dtype=int)
        if candidate.size == dim:
            candidates.append(candidate)
    return np.array(candidates, dtype=int)


def convert_seeds_unicode_step(dim: int, seeds: list[bytes]) -> np.array:
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
        candidate = np.array(temp, dtype=int)
        if candidate.size == dim:
            candidates.append(candidate)
    return np.array(candidates, dtype=int)



