"""
Defines functions to create parameters data points for fully random distribution
"""
import logging
import random
import numpy as np
from qcgpilotnetsquid.utils.parserconstraints import evaluate_constraints


def make_init_datapoints_random(sim_param, set_param):
    """Make a fully random sample of points.

    Constraints are evaluated to ensure that the returned array has the desired size
    and all points satisfy the constraints.

    Parameters
    ----------
    set_params : smartstopos.utils.SetParameters object

    Returns
    -------
    list_points
    """
    logging.debug("Making random set of initial points")
    for param in set_param.parameters.values():
        del param.data_points[:]

    number_points = 1
    for param in set_param.parameters.values():
        number_points = param.number_points * number_points

    population = []
    while len(population) < number_points:
        points = np.random.random((number_points, len(set_param.parameters)))

        for index, param in enumerate(set_param.parameters.values()):
            points[:, index] = points[:, index] * (param.range[1] - param.range[0]) + param.range[0]
            if param.data_type == 'discrete':
                points[:, index] = np.floor(points[:, index])

        points = evaluate_constraints(sim_param, set_param, points)
        population.extend(points.tolist())

    if len(population) > number_points:
        population = random.sample(population, number_points)

    return population
