""" Implmentation of random displacements"""
import os
import logging
import random
import copy
from pprint import pformat
import numpy as np

def random_displacement(data, set_param, sim_param, step):
    """
    Parameters
    ----------
    data : list (arrays)
        Array with the data points corresponding to the fittest and their
        mutations.
    set_param : :obj:`smartstopos.utils.parameters.set_parameters`
        Set parameters to be explored
    sim_param: dict
        Simulation information read from input file
    step: int
        Optimization step

    Returns
    -------
    test_points: list of arrays
        New set of data points to be explored. Each data point is a set of parameter values
    """
    if not isinstance(data, list):
        raise TypeError("Data must be a list")
    
    #if sim_params['maximum']:
    #    data_sorted = np.array(sorted(data, key=lambda x: x[0], reverse=True))
    #else:
    #    data_sorted = np.array(sorted(data, key=lambda x: x[0]))

    datapoints = []
    for item in data:
        datapoints.append(item[1:])

    random.seed(sim_param['seed'])
    test_points = []
    number_parameters = sim_param['number_parameters']

    if number_parameters == 1:
        param = set_param.parameters[0]
        for point in current_points:
            while True:
                delta = random.random.uniform(-1,1)*param.scale_factor   
                testpoint = point + delta
                if testpoint > param.range[0] and testpoint < param.range[1]:
                    if param.data_type == 'discrete':
                        test_points.append(np.array(testpoint, dtype=int))
                    else:
                        test_points.append(np.array(testpoint, dtype=float))
                    break

    elif number_parameters > 1:
        for point in datapoints: 
            testpoint = []
            for i, param in enumerate(set_param.parameters.values()):
                while True:
                    delta = random.uniform(-1,1)*param.scale_factor
                    test = point[i] + delta
                    if test > param.range[0] and test < param.range[1]:
                        if param.data_type == 'discrete':
                            testpoint.append(np.array(test, dtype=int))
                        else:
                            testpoint.append(np.array(test, dtype=float))
                        break
            test_points.append(np.array(testpoint, dtype=float))
    return test_points
