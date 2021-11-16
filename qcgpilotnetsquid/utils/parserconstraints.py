"""Define a parser of constraints."""
import numpy as np


def evaluate_constraints(sim_param, set_param, population):
    """Remove from the given population all individuals not satisfying the constraints."""
    if 'constraints' in sim_param.keys():
        params = {}
        for key, item in set_param.parameters.items():
            params[key] = 0

        conditions = sim_param['constraints']
        # new_population = copy.copy(population)
        to_keep = []
        for index, item in enumerate(population):
            for p, name in enumerate(set_param.parameters.keys()):
                params[name] = item[p]

            if eval(conditions, params):
                to_keep.append(index)

        if isinstance(population, np.ndarray):
            return population[to_keep]
        else:
            return [population[i] for i in to_keep]

    return population
