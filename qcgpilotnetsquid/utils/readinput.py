"""Read input file"""
import json
import random
from argparse import ArgumentParser
from qcgpilotnetsquid.utils.parameters import Parameter, SetParameters


def str2bool(v):
    return v.lower() in ("True", "yes", "true", "t", "1")

def read_input_json(filename):
    """Read input file in json format. 
    
Parameters
    ----------
    filename : str
        Name of the input file

    Returns
    -------
    sim_parameters : dict
        A dictionary with the parameters needed for the simulations as read from
        input file.
    set_parameters : smartstopos.utils.parameter.SetParameters
        Set of parameters and their properties as read from the input file.
    """
    sim_parameters = {'number_best_candidates': 10, 'proba_mutation': 1.0,
                 'proba_crossover': 1.0, 'global_scale_factor': 1.0, 'maximum':
                 False, 'seed': random.random(), 'run_type': 'single',
                 'algorithm': None, 'distribution': None}

    
    parameters = False
    set_parameters = SetParameters()

    # defaults for some optimization algorithms. Still needed?
    scale_factor = 1.0
    width_distribution = 1.0
    p_weight = 1.0
    sim_parameters['global_width_distribution'] = 1.0
    sim_parameters['global_scale_factor'] = 1.0

    # Using readlines()
    f = open(filename, 'r')
    data = json.load(f)
    general = data['general']
    parameters = data['parameters']
    run = general['run']
        
    sim_parameters['number_parameters'] = int(run['number_parameters'])
    sim_parameters['seed'] = float(run['seed'])
    if 'constraints' in run.keys():
        sim_parameters['constraints'] = compile(run['constraints'], 'constraints', 'eval')
   
    if 'optimization' in run['type'].keys(): 
        sim_parameters['run_type']='optimization'
        sim_parameters['algorithm'] = run['type']['optimization']
        sim_parameters['opt_steps'] = int(run['type']['steps'])
        sim_parameters['maximum'] = str2bool(run['type']['maximum'])
        sim_parameters['proba_mutation'] = float(run['type']['algorithm']['probability_mutation'])
        sim_parameters['proba_crossover']= float(run['type']['algorithm']['probability_crossover'])
        sim_parameters['number_best_candidates']= int(run['type']['algorithm']['number_best_candidates'])
        sim_parameters['population_size']=int(run['type']['algorithm']['population_size'])

        # optimization algorithm
        if run['type']['algorithm']['order']:
            order = run['type']['algorithm']['order']
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

        # local optimization
        if run['type']['localopt']:
            localopt = run['type']['localopt']['algorithm']
            if localopt not in ["random", "NM", "gradient"]:
                raise TypeError("local optimization algorithm is not defined")
            else:
                sim_parameters['localopt'] = localopt
                sim_parameters['lsteps'] = run['type']['localopt']['steps']

        #sim_parameters['distribution']= run['distribution']
        
    elif 'single' in run['type'].keys(): 
        sim_parameters['run_type']='single'
    else:
        raise ValueError("Run type error. Please chose between single or optimization")


    for item in parameters:
        minimal_requirements = {'min': False,
                                'max': False,
                                'num_points': False,
                                'distribution': False,
                                'type': False
                                }
        width_distribution = sim_parameters['global_width_distribution']
        scale_factor = sim_parameters['global_scale_factor']
        p_weight = 1.0
        name = item['name']
        if 'max' in item.keys():
            minimal_requirements['max'] = True
            maxr = float(item['max'])
        if 'min' in item.keys():
            minimal_requirements['min'] = True
            minr = float(item['min'])
        if 'number_points' in item.keys():
            minimal_requirements['num_points'] = True
            num_points = int(item['number_points'])
        if 'distribution' in item.keys():
            dist = str(item['distribution'])
            minimal_requirements['distribution'] = True
            valid_distributions = ["uniform", "log", "random", "normal"]
            if dist not in valid_distributions:
                raise ValueError("Distribution not define. "
                                 "Please chose an existing one or define your own in makedatapoints.py")
        if 'type' in item.keys():
            typep = str(item['type'])
            if typep not in ["discrete", "continuous"]:
                raise ValueError("Data type of parameter {} is not valid. "
                                 "Please chose between discrete and continuous".format(name))
            minimal_requirements['type'] = True
        if 'scale_factor' in item.keys():
            scale_factor = float(item['scale_factor'])
        if 'width_distribution' in item.keys():
            width_distribution = float(item['width_distribution'])
        if 'weight' in item.keys():
            p_weight = float(item['weight'])
        if minr > maxr:
            raise ValueError("The minimum value is larger than the maximum for parameter '{}'".format(name))
        if all(minimal_requirements):
            set_parameters.add_parameter(Parameter(name, [minr, maxr],
                                         num_points, typep, dist, scale_factor,
                                         width_distribution, variance=0.0,
                                         weight=p_weight, active=True))

        else:
            raise ValueError("One or more of the minimal requirements (min, max, number_point, type, dsitribution) "
                             "for parameter {} is not defined".format(name))
    
    return sim_parameters, set_parameters

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('--input_file', required=False, default="input_file.json", type=str,
                        help='File with the input information about the simulation and parameters')
    args = parser.parse_args()
    sim_params, set_params = read_input_json(args.input_file)
    print(sim_params)
    print(set_params)
