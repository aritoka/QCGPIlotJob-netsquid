"""Defines functions to create parameters data points based on number points and distribution selected."""
import numpy as np
import math
import random
import sys


def make_data_points(set_param):
    """Based on the type of distribution, parameter type, range and number of points it
    creates an intitial set of data points to be explored.

    Parameters
    ----------
    set_param : smartstopos.utils.SetParameters object
    """
    for param in set_param.parameters.values():
        del param.data_points[:]

        if param.data_type == "continuous":
            if param.distribution == 'uniform':
                if param.number_points > 1:
                    interval = abs(param.range[0] - param.range[1]) / (param.number_points - 1)
                    for i in range(0, param.number_points):
                        param.data_points.append(param.range[0] + i * interval)
                else:
                    param.data_points.append(param.range[0])

            elif param.distribution == 'log':
                if param.range[0] <= 0 or param.range[1] <= 0:
                    raise ValueError("Logarithm of one of the range boundaries is not defined")
                    sys.exit(0)
                else:
                    if param.number_points > 1:
                        param.data_points = np.logspace(np.log10(param.range[0]), np.log10(param.range[1]),
                                                        num=param.number_points)
                    else:
                        param.data_points.append(param.range[0])

            elif param.distribution == 'random':
                for i in range(0, param.number_points):
                    value = random.random()*(param.range[1] - param.range[0]) + param.range[0]
                    param.data_points.append(value)

            # any distribution can be added like this
            elif param.distribution == 'normal':
                mean = 0.5*(param.range[1] - param.range[0])
                size = (param.range[1] - param.range[0])/5.0
                # print ("mean normal: {}".format(mean))
                # print ("variance normal: {}".format(size))
                for i in range(0, param.number_points):
                    while True:
                        value = float(np.random.normal(loc=mean, scale=size, size=1))
                        if value > param.range[1] or value < param.range[0]:
                            break
                    param.data_points.append(value)
            else:
                raise ValueError("{}: this distribution type is not defined for a continuous variable. "
                                 "Please choose among: uniform, random, log, normal".format(param.distribution))
                sys.exit(0)

        elif param.data_type == "discrete":
            if param.distribution == 'uniform':
                if param.number_points == 1:
                    param.data_points.append(param.range[0])
                else:
                    interval = abs(param.range[0] - param.range[1]) / (param.number_points - 1)
                    for i in range(0, param.number_points):
                        param.data_points.append(param.range[0] + math.ceil(i*interval))
            elif param.distribution == 'log':
                if param.range[0] <= 0 or param.range[1] <= 0:
                    raise ValueError("Logarithm of one of the range boundaries is not defined")
                    sys.exit(0)
                else:
                    if param.number_points > 1:
                        param.data_points = np.logspace(np.log10(param.range[0]), np.log10(param.range[1]),
                                                        num=param.number_points)
                        param.data_points.astype(int)
                    else:
                        param.data_points.append(param.range[0])
            elif param.distribution == 'random':
                for i in range(0, param.number_points):
                    value = int(random.random()*(param.range[1] - param.range[0]) + param.range[0])
                    param.data_points.append(value)

            # any distribution can be added like this
            elif param.distribution == 'normal':
                mean = 0.5*(param.range[1] - param.range[0])
                size = (param.range[1] - param.range[0])/5.0
                # print("mean normal: {}".format(mean))
                # print("variance normal: {}".format(size))
                for i in range(0, param.number_points):
                    while True:
                        value = int(np.random.normal(loc=mean, scale=size, size=1))
                        if value < param.range[1] or value > param.range[0]:
                            break
                    param.data_points.append(value)
            else:
                raise ValueError("{}: this distribution type is not defined for a discrete variable. "
                                 "Please choose among: uniform, random, log, normal".format(param.distribution))
                sys.exit(0)
        else:
            raise ValueError("Parameter data type {} does not exist; should be either discrete or continuous"
                             .format(param.data_type))
            sys.exit(0)
