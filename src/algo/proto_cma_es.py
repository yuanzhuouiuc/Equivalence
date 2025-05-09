import cma
import math
import numpy as np
from typing import List
import src.diff_oracle.protobuf.proto_buf as proto_buf

class PROTO_CMA_ES:
    def __init__(self, x0: np.array, objective_function: callable, bounds: tuple[np.ndarray, np.ndarray],
                 field_info: List, handler: proto_buf.ProtobufHandler):
        """
        Initialize CMA-ES optimizer with a single starting point and dimension-specific bounds.

        Args:
            x0: Initial solution vector
            objective_function: Function to be optimized
            bounds: Either (lower_bound, upper_bound) for uniform bounds,
                  or ([lower_bound_1, lower_bound_2, ...], [upper_bound_1, upper_bound_2, ...])
                  for dimension-specific bounds
        """
        self._seed = x0
        self._dim = len(x0)
        self.obj_func = objective_function

        # Handle different types of bounds
        lower_bounds, upper_bounds = bounds
        self._lower_bound = np.array(lower_bounds)
        self._upper_bound = np.array(upper_bounds)
        self._penalty_coefficient = 1.0e+6

        self._field_info = field_info
        self._proto_handler = handler

        if len(self._lower_bound) != self._dim or len(self._upper_bound) != self._dim:
            raise ValueError(f"Bounds must have length equal to dimension ({self._dim})")

    def _objective_function(self, x):
        """
        Wrapper for the objective function. Converts continuous values to integers
        and returns negative absolute difference for minimization.

        Args:
            x: Solution vector to evaluate
        Returns:
            Negative absolute difference (for minimization)
        """
        try:
            if np.any(np.isnan(x)):
                return self._penalty_coefficient
            x = np.clip(np.rint(x), self._lower_bound, self._upper_bound)
            # convert vector to raw bytes for execution
            proto_bytes = self._proto_handler.vector_to_protobuf(x, self._field_info)
            if not self._proto_handler.is_valid_msg(proto_bytes):
                return self._penalty_coefficient
            diff, c_cov = self.obj_func(proto_bytes)
            return -abs(diff)
        except Exception as e:
            return self._penalty_coefficient

    def run(self, num_iterations: int = 1, popsize: int = 2000):
        """
        Run the CMA-ES algorithm.

        Args:
            num_iterations: Number of independent CMA-ES runs
            popsize: Population size for CMA-ES

        Returns:
            Tuple of (best_solution, best_objective_value)
        """
        opts = {
            'popsize': popsize,
            'CMA_mu': popsize // 2,
            'CMA_active': True,
            'bounds': [self._lower_bound.tolist(), self._upper_bound.tolist()],
            'maxiter': 50,  # max iterations
            'minstd': 1e-3,
            'verb_disp': 1,
            'verb_log': 0,
            'tolfun': 1e-6,
            'CMA_diagonal': True
        }

        best_overall_solution = None
        best_overall_value = float('inf')

        for i in range(num_iterations):
            # Use the provided seed
            x0 = self._seed
            sigma = 10  # Initial step size
            # Initialize CMA-ES
            es = cma.CMAEvolutionStrategy(x0, sigma, opts)
            # Run optimization for specified generations
            NGEN = 50  # generations
            for gen in range(NGEN):
                solutions = es.ask()
                fitnesses = [self._objective_function(sol) for sol in solutions]
                es.tell(solutions, fitnesses)
                es.disp()
            # Get best solution from this run
            best_solution = np.rint(es.result.xbest).astype(int)
            best_value = es.result.fbest
            print(f"CMA-ES Run {i + 1} best solution:")
            print(best_solution)
            print(f"Objective value: {best_value}")
            # Update best overall if better
            if best_value < best_overall_value:
                best_overall_value = best_value
                best_overall_solution = best_solution
        print("Overall best solution:")
        print(best_overall_solution)
        print(f"Overall objective value: {best_overall_value}")

        return best_overall_solution, best_overall_value