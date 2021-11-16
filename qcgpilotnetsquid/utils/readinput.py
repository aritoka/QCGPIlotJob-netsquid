"""Read input file"""
import json
import random
from argparse import ArgumentParser
from qcgpilotnetsquid.utils.parameters import Parameter, SetParameters


def str2bool(v):
    return v.lower() in ("True", "yes", "true", "t", "1")

#----------- deprecated-----------------
def read_input(filename, sim_parameters):
    """Read input file for smartstopos.

    Parameters
    ----------
    filename : str
        Name of the input file
    sim_parameters : dict
        A dictionary with the parameters needed for the simulations as read from
        input file.

    Returns
    -------
    set_parameters : smartstopos.utils.parameter.SetParameters
        Set of parameters and their properties as read from the input file.
    """
    parameters = False
    set_parameters = SetParameters()
    sim_info = False

    # defaults for some optimization algorithms. Still needed?
    scale_factor = 1.0
    width_distribution = 1.0
    p_weight = 1.0
    sim_parameters['global_width_distribution'] = 1.0
    sim_parameters['global_scale_factor'] = 1.0

    with open(filename, "r") as f:
        lines = [line.strip() for line in f.readlines()]
    for line in lines:
        variable = line.split(":")[0].strip()
        if line == 'GENERAL':
            sim_info = True
        elif line == 'END_GENERAL':
            sim_info = False
        if sim_info:
            if variable == 'run_type':
                value = line.split(":")[1]
                if value.split()[0] not in ["single", "optimization"]:
                    raise ValueError("Run type error. Please chose between single or optimization")
                else:
                    sim_parameters['run_type'] = value.split()[0]

                if value.split()[0] == 'optimization':
                    if len(value.split()) < 3:
                        raise ValueError("run_type optimization minimal arguments:\n run_type: "
                                         "optimization algorithm opt_steps\n If not specified, "
                                         "it will perform a normal selection mechanism and corssover before mutation.")
                    sim_parameters['algorithm'] = value.split()[1]
                    sim_parameters['opt_steps'] = int(value.split()[2])
                    if len(value.split()) > 3:
                        if value.split()[3] == 'c':
                            sim_parameters['c'] = True
                        elif value.split()[3] == 'm':
                            sim_parameters['m'] = True
                        elif value.split()[3] == 'cr':
                            sim_parameters['c'] = True
                            sim_parameters['roulette'] = True
                        elif value.split()[3] == 'mr':
                            sim_parameters['m'] = True
                            sim_parameters['roulette'] = True
                    # default GA is c
                    else:
                        sim_parameters['c'] = True
                    if 'roulette' not in sim_parameters:
                        sim_parameters['roulette'] = False
            elif variable == 'localopt':
                value = line.split(":")[1]
                if value.split()[0] not in ["random", "NM", "gradient"]:
                    raise ValueError("local optimization algorithm is not defined")
                else:
                    sim_parameters['localopt'] = value.split()[0]
                    sim_parameters['lsteps'] = value.split()[1]

            elif variable == 'global_scale_factor':
                value = float(line.split(":")[1].strip())
                sim_parameters['global_scale_factor'] = value
                scale_factor = sim_parameters['global_scale_factor']
            elif variable == 'distribution':
                value = line.split(":")[1].strip()
                if value == "fully_random":
                    print("WARNING: using fully_random in the general settings overwrites "
                          "any distribution choice at parameters level")
                sim_parameters['distribution'] = value
            elif variable == 'proba_mutation':
                value = float(line.split(":")[1].strip())
                sim_parameters['proba_mutation'] = value
            elif variable == 'proba_crossover':
                value = float(line.split(":")[1].strip())
                sim_parameters['proba_crossover'] = value
            elif variable == 'number_parameters':
                value = int(line.split(":")[1].strip())
                sim_parameters['number_parameters'] = value
            elif variable == 'maximum' or variable == 'Maximum':
                sim_parameters['maximum'] = str2bool(str(line.split(":")[1].strip()))
            elif variable == 'seed':
                sim_parameters['seed'] = float(line.split(":")[1].strip())
            elif variable == 'number_best_candidates':
                sim_parameters['number_best_candidates'] = int(line.split(":")[1].strip())
            elif variable == 'global_width_distribution':
                sim_parameters['global_width_distribution'] = float(line.split(":")[1].strip())
                width_distribution = sim_parameters['global_width_distribution']
            elif variable == 'population_size':
                print("WARNING: population size does not apply in single runs or first optimization step")
                value = int(line.split(":")[1].strip())
                sim_parameters['population_size'] = value
            elif variable == 'constraints':
                value = line.split(":")[1].strip()
                sim_parameters['constraints'] = compile(value, 'constraints', 'eval')

        if variable == 'Parameter':
            parameters = True
            minimal_requirements = {'min': False,
                                    'max': False,
                                    'num_points': False,
                                    'distribution': False,
                                    'type': False
                                    }
            width_distribution = sim_parameters['global_width_distribution']
            scale_factor = sim_parameters['global_scale_factor']
            p_weight = 1.0
        if parameters:
            if variable == 'name':
                name = str(line.split(":")[1].strip())
            elif variable == 'max':
                minimal_requirements['max'] = True
                maxr = float(line.split(":")[1].strip())
            elif variable == 'min':
                minimal_requirements['min'] = True
                minr = float(line.split(":")[1].strip())
            elif variable == 'number_points':
                minimal_requirements['num_points'] = True
                num_points = int(line.split(":")[1].strip())
            elif variable == 'distribution':
                dist = str(line.split(":")[1].strip())
                minimal_requirements['distribution'] = True
                valid_distributions = ["uniform", "log", "random", "normal"]
                if dist not in valid_distributions:
                    raise ValueError("Distribution not define. "
                                     "Please chose an existing one or define your own in makedatapoints.py")
            elif variable == 'type':
                typep = str(line.split(":")[1].strip())
                if typep not in ["discrete", "continuous"]:
                    raise ValueError("Data type of parameter {} is not valid. "
                                     "Please chose between discrete and continuous".format(name))
                minimal_requirements['type'] = True
            elif variable == 'scale_factor':
                scale_factor = float(line.split(":")[1].strip())
            elif variable == 'width_distribution':
                width_distribution = float(line.split(":")[1].strip())
            elif variable == 'weight':
                p_weight = float(line.split(":")[1].strip())

        if parameters and line.rstrip() == 'end':
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
            parameters = False
    return set_parameters


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

        sim_parameters['distribution']= run['distribution']
        
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

 
