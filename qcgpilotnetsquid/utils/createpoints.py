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
from qcgpilotnetsquid.algorithms.ga import genetic_algorithm 
from qcgpilotnetsquid.algorithms.randomdisplacement import random_displacement
from qcgpilotnetsquid.utils.readcsv import readcsvfiles
from qcgpilotnetsquid.utils.readinput import read_input_json
from qcgpilotnetsquid.utils.makedatapoints import make_data_points
from qcgpilotnetsquid.utils.makedatapoints_random import make_init_datapoints_random
from qcgpilotnetsquid.utils.parserconstraints import evaluate_constraints

def str2bool(v):
    return v.lower() in ("True", "yes", "true", "t", "1")

# to match current GA implementation 
def run_param_to_sim_param(run_param, opt):
    sim_parameters = {}
    sim_parameters['number_parameters'] = int(run_param['number_parameters'])
    sim_parameters['seed'] = float(run_param['seed'])
    if 'constraints' in run_param.keys():
        sim_parameters['constraints'] = compile(run_param['constraints'], 'constraints', 'eval')
   
    if run_param['type'] == "optimization":
        sim_parameters['run_type']='optimization'
        sim_parameters['algorithm'] = run_param['algorithm'][opt]['name']
        sim_parameters['opt_steps'] = int(run_param['algorithm'][opt]['steps'])
        sim_parameters['maximum'] = str2bool(run_param['maximum'])
        if sim_parameters['algorithm'] == "GA":
            sim_parameters['proba_mutation'] = float(run_param['algorithm'][opt]['parameters']['probability_mutation'])
            sim_parameters['proba_crossover']= float(run_param['algorithm'][opt]['parameters']['probability_crossover'])
            sim_parameters['number_best_candidates']=int(run_param['algorithm'][opt]['parameters']['number_best_candidates'])
            sim_parameters['population_size']=int(run_param['algorithm'][opt]['parameters']['population_size'])

            # optimization algorithm
            if run_param['algorithm'][opt]['parameters']['order']:
                order = run_param['algorithm'][opt]['parameters']['order']
                if order == 'c':
                    sim_parameters['c'] = True
                elif order == 'm':
                    sim_parameters['m'] = True
                elif order == 'cr':
                    sim_parameters['c'] = True
                    sim_parameters['roulette'] = True
                elif order == 'mr':
                    sim_parameters['m'] = True
                    sim_parameters['roulette'] = True
                else:
                    sim_parameters['c'] = True
                    if 'roulette' not in sim_parameters:
                        sim_parameters['roulette'] = False
        sim_parameters['distribution']= run_param['distribution']
        
    elif 'single' in run_param['type'].keys(): 
        sim_parameters['run_type']='single'
    else:
        raise ValueError("Run type error. Please chose between single or optimization")
    return sim_parameters


def create_datapoints(simparameters, step, opt):
    """Create data points to explore, either based on input file or using
    previous csvfiles
    Parameters
    ----------
    simparameters : class InputParam()
        Simulation information read from input file
    step: int
        Previous optimization step
    opt: int
        When many optimization algorithms, the number associated to the
optimization

    Returns
    -------
    newdatapoints : list of arrays
        New set of data points to be explored. Each data point is a set of
        parameters values of length = number parameters.
    """
    # current fix for GA implementation
    sim_param = run_param_to_sim_param(simparameters.run, opt)
    set_param = simparameters.param

    backsteps = 0 
    if step == 0 and simparameters.restart == False:
        print("Simulation not restarted from a previous csvfile, creating initial data points based on input file information")
        if sim_param['distribution'] == 'fully_random':
            newdatapoints  = make_data_points_random(sim_param, set_param)
        else:
            make_data_points(set_param)
            newdatapoints = create_init_datapoints(sim_param, set_param)

    # create data points based on csvfile(s)
    # backsteps: how many previous opt steps csv_files should be read,
    elif step == 0 and simparameters.restartcsvfile == True:
        if simparameters.restartcsvfile is None:
            raise NameError('You need to give a path to a directory containing \
                           a csv file to restart from')
        else:
            print("Simulation restarted from: {}, reading\
                 csvfile".format(restartcsvfile))

    elif step == 1:
        backsteps = 1

    elif step == 2:
        backsteps = 2

    elif step > 2:
        backsteps = 3

    totaldata = readcsvfiles(simparameters, step, backsteps, subsample=None)

    # create data points based on information read from csvfiles
    algorithm = simparameters.algorithm
    if step > 0 or simparameters.restart == True:
        if algorithm == 'random':
            # todo random check req.
            # algorithm self check?
            newdatapoints = random_displacement(totaldata[0], set_param, sim_param, step)
        elif algorithm == 'GA':
            # todo GA check req.
            print("Calling {} algorithm...".format(algorithm))
            newdatapoints = genetic_algorithm(totaldata[0], set_param, sim_param, step)
        elif algorithm == 'Gaussians':
            newdatapoints = gaussian(totaldata, set_param, sim_param, step)
        elif algorithm == 'NM':
            newdatapoints = NelderMead(totaldata, set_param, sim_param, step)
        elif algorithm == 'gradient':
            newdatapoints = GradientBased(totaldata, set_param, sim_param, step)
        else:
            raise TypeError("no algorithm defined")

    # Create a new param_set_optstep file 
    with open(simparameters.rundir + "param_set_" + str(step), "w") as paramfile:
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
        print("Checking constraints...")
        new_points = evaluate_constraints(sim_param, set_param, points)
        if len(new_points) != len(points):
            raise ValueError("Some global constraints are not satisfied, check your initial parameter settings")
            
    else:
        new_points = points
    return new_points

#def main():
#    parser = ArgumentParser()
#    parser.add_argument('--inputfile', required=True, type=str, 
#                        help='File with the input information about the simulation and parameters')
#    parser.add_argument('--algorithm', required=True, type=str, 
#                        help='Algorithm for optimization')
#    parser.add_argument('--csvfiledir', required=True, type=str,
#                        help='Directory with csvfile to use')
#    parser.add_argument('--optdir', required=True, type=str,
#                        help='Directory /optimization')
#    parser.add_argument('--csvprefix', required=False, default="csv_output",
#                        type=str, help="prefix of csvfiles")
#    parser.add_argument('--step', required=True, type=int)
#    args = parser.parse_args()
#    
#    sim_param, set_param = read_input_json(arg.inputfile)
#
#    create_datapoints(sim_param, set_param, arg.algorithm, args.csvfiledir, args.csvprefix,
#                     args.optdir, args.step, restart=False)
#    
#if __name__ == "__main__":
#    main()
