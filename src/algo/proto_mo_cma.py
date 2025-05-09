import random
import numpy as np
from typing import List
from deap import base, creator, tools
from deap.cma import StrategyMultiObjective
import src.diff_oracle.protobuf.proto_buf as proto_buf

class PROTO_MO_CMA_ES:

    def __init__(self, dim: int, seed_population: np.array, objective_function: callable, bounds: (np.ndarray, np.ndarray),
                 field_info: List, proto_handler: proto_buf.ProtobufHandler):
        """
        :param dim: vector dimension
        :param seed_population: initial population, shape: (n, dim)
        :param objective_function: objective function, return diff, code coverage
        """
        self._dim = dim
        self._seed_population = seed_population
        self._obj_func = objective_function
        self._lambda = min(200, len(self._seed_population))
        self._mu = self._lambda // 2
        self._proto_handler = proto_handler
        self._field_info = field_info

        lower_bounds, upper_bounds = bounds
        if len(lower_bounds) == dim and len(upper_bounds) == dim:
            self._lower_bound = lower_bounds
            self._upper_bound = upper_bounds
        else:
            raise ValueError(
                "Bounds must be either a tuple of (lower, upper) arrays or a list of (lower, upper) tuples for each dimension")
        # Penalty coefficient for boundary violations
        self._penalty_coefficient = 1.0e+6

    def _enforce_bounds(self, individual):
        """Enforce bounds on an individual"""
        arr = np.array(individual)
        arr = np.maximum(self._lower_bound, arr)
        arr = np.minimum(self._upper_bound, arr)
        individual[:] = arr.tolist()
        return individual

    def _enforce_bounds_population(self, population):
        """Enforce bounds on all individuals in a population"""
        for ind in population:
            self._enforce_bounds(ind)
        return population

    def _evaluate(self, x):
        proto_bytes = self._proto_handler.vector_to_protobuf(x, self._field_info)
        if not self._proto_handler.is_valid_msg(proto_bytes):
            return (-self._penalty_coefficient, -1.0)
        diff, c_cov = self._obj_func(proto_bytes)
        return (abs(diff), c_cov)

    def _validity(self, ind):
        proto_bytes = self._proto_handler.vector_to_protobuf(ind, self._field_info)
        if not self._proto_handler.is_valid_msg(proto_bytes):
            return False
        arr = np.array(ind)
        return np.all(arr >= self._lower_bound) and np.all(arr <= self._upper_bound)

    def _feasible(self, ind):
        arr = np.array(ind)
        arr = np.maximum(self._lower_bound, arr)
        arr = np.minimum(self._upper_bound, arr)
        return arr.tolist()

    def _distance(self, feasible_ind, original_ind):
        return sum((f - o) ** 2 for f, o in zip(feasible_ind, original_ind))

    def _bounded_generate(self, strategy, ind_class):
        """Custom generation function that respects dimension-specific bounds"""
        individuals = strategy.generate(ind_class)
        return self._enforce_bounds_population(individuals)

    def _bounded_update(self, strategy, population):
        """Custom update function that ensures bounds are respected after update"""
        strategy.update(population)
        self._enforce_bounds_population(population)

    def _setup(self):
        # Reset creator to avoid DuplicateNames error in case of restart
        if "FitnessMulti" in creator.__dict__:
            del creator.FitnessMulti
        if "Individual" in creator.__dict__:
            del creator.Individual
        creator.create("FitnessMulti", base.Fitness, weights=(1.0, 0.1))
        creator.create("Individual", list, fitness=creator.FitnessMulti)

        toolbox = base.Toolbox()
        toolbox.register("evaluate", self._evaluate)
        # register penalty function
        toolbox.decorate("evaluate", tools.ClosestValidPenalty(self._validity,
                                                               self._feasible,
                                                               self._penalty_coefficient,
                                                               self._distance))

        pop = self._init_pop()
        for ind in pop:
            ind.fitness.values = toolbox.evaluate(ind)
        strategy = StrategyMultiObjective(pop, sigma=10000, lambda_=self._lambda, mu=self._mu)
        # toolbox.register("generate", strategy.generate, creator.Individual)
        # toolbox.register("update", strategy.update)

        # Register bounded generation and update functions
        toolbox.register("generate", self._bounded_generate, strategy)
        toolbox.register("update", self._bounded_update, strategy)

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