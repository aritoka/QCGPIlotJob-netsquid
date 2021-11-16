""" create datapoints to explore in a simulation"""
import itertools
import os
import logging
import random
import sys
import copy
import numpy as np
import pandas as pd
import pprint
from argparse import ArgumentParser
from smartstopos.algorithms.ga import genetic_algorithm 
from smartstopos.algorithms.randomdisplacement import random_displacement
from smartstopos.utils.readcsv import readcsvfiles
from smartstopos.utils.readinput import read_input_json
from smartstopos.utils.makedatapoints import make_data_points
from smartstopos.utils.makedatapoints_random import make_init_datapoints_random
from smartstopos.utils.parserconstraints import evaluate_constraints


def create_datapoints(sim_param, set_param, algorithm, csvfiledir, csvprefix, optdir, step,
                     restartcsv, restart=False):
    """Create data points to explore, either based on input file ro using last
csvfile and optimization algorithm
    Parameters
    ----------
    sim_param : dict
        Simulation information, parameters for algorithm
    set_param : smartstopos object
        Set parameters to be explored
    algorithm : string
        Optimization algorithm
    csvfiledir: string
        Default == None, else directory with the csv files with results of previous runs
    csvprefix: string
        prefix of csv files with results
    optdir: string
        Directory /optimization/
    step: int
        Last optimization step
    restartcsv: string
        In case of a restart, csvfile from whcih to start
    restart: bool   
        True is the step is a restart of a previous optimization run

    Returns
    -------
    newdatapoints : list of arrays
        New set of data points to be explored. Each data point is a set of
        parameters values of length = number parameters.
    """
    # create datapoints based on information in input file
    # TODO: come up with a simpler way
    if step == 0 and restart == False:
        print("Simulation not restarted from a previous csvfile, creating initial data points")
        if sim_param['distribution'] == 'fully_random':
            newdatapoints  = make_data_points_random(sim_param, set_param)
        else:
            make_data_points(set_param)
            newdatapoints = create_init_datapoints(sim_param, set_param)
    
    # create data points based on csvfile(s)
    # read csvfiles
    backsteps=step
    if step == 0 and restart == True:
        print("Simulation restarted from: {}, reading csvfile".format(restartcsv))
        if restartcsv is not None:
            restartcsv=restartcsv
        else: 
            raise NameError('You need to give a path to a restart csv file')
    elif step == 1 or step == 2:
        restartcsv=None
    elif step > 2:
        backsteps=3
        restartcsv=None
    
    totaldata = readcsvfiles(csvfiledir, optdir, csvprefix, step,
                                 backsteps, restartcsv, subsample=None)
    
    # create data points based on information read from csvfiles
    if step > 0 or restart==True:
        if algorithm == 'random':
            newdatapoints = random_displacement(totaldata[0], set_param,
                                                sim_param, step)
        elif algorithm == 'GA':
            newdatapoints = genetic_algorithm(totaldata[0], set_param, sim_param,
                                             step)
        elif algorithm == 'Gaussians':
            newdatapoints = gaussian(totaldata, set_param, sim_param, step)
        elif algorithm == 'NM':
            newdatapoints = NelderMead(totaldata, set_param, sim_param, step)
        elif algorithm == 'gradient':
            newdatapoints = GradientBased(totaldata, set_param, sim_param, step)
        else:
            raise TypeError("no algorithm defined")

    # Create a new param_set_optstep file 
    with open(optdir + "param_set_" + str(step), "w") as paramfile:
        for point in newdatapoints:
            for item in point:
                paramfile.write("{} ".format(item))
            paramfile.write("\n")
    return newdatapoints


def create_init_datapoints(sim_param, set_param):
    """Creates initial data points.

    Parameters
    ----------
    sim_params : dict
        Dictionary with the simulation details read from the input file.
    set_param : smartstopos.utils.parameters.SetParameters
        Set of parameters to be explored during the simulations. Data points of
        the simulation are created from these parameters.
    """
    all_data_points = []
    for _key, param in set_param.parameters.items():
        if param.data_type == "discrete":
            param.data_points = list(map(int, param.data_points))
            all_data_points.append(param.data_points)
        elif param.data_type == 'continuous':
            all_data_points.append(param.data_points)
        else:
            raise ValueError("data type of one of the parameters does not exist")
    points = []
    for item in itertools.product(*all_data_points):
        points.append(item)
    if 'constraints' in sim_param.keys():
        print("\nChecking constraints...")
        new_points = evaluate_constraints(sim_param, set_param, points)
        if len(new_points) != len(points):
            print("Some global constraints are not satisfied, check your initial parameter settings")
    else:
        new_points = points
    return new_points

def main():
    parser = ArgumentParser()
    parser.add_argument('--inputfile', required=True, type=str, 
                        help='File with the input information about the simulation and parameters')
    parser.add_argument('--algorithm', required=True, type=str, 
                        help='Algorithm for optimization')
    parser.add_argument('--csvfiledir', required=True, type=str,
                        help='Directory with csvfile to use')
    parser.add_argument('--optdir', required=True, type=str,
                        help='Directory /optimization')
    parser.add_argument('--csvprefix', required=False, default="csv_output",
                        type=str, help="prefix of csvfiles")
    parser.add_argument('--step', required=True, type=int)
    args = parser.parse_args()
    
    sim_param, set_param = read_input_json(arg.inputfile)

    create_datapoints(sim_param, set_param, arg.algorithm, args.csvfiledir, args.csvprefix,
                     args.optdir, args.step, restart=False)
    
if __name__ == "__main__":
    main()
