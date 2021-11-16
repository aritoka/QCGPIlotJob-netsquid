""" Implmentation of genetic algorithm for N-parameters."""
import logging
import random
import copy
from pprint import pformat
from smartstopos.utils.parserconstraints import evaluate_constraints
# from pprint import pprint
import numpy as np


def get_parents(data, sim_params):
    """Selects the N=number_best_candidates data points from the data based on their fitness.

    Parameters
    ----------
    data : list
        List of the data points read from output file of previous step.
    sim_params : dict
        Dictionary with the simulation details read from the input file.

    Returns
    -------
    best_candidates: list (arrays)
        Returns list of best_candidates.
    fitness: list
        The fitness values of the best_candidates (same order as best_candidates
        list)
    sorted_data: list (arrays)
        List of all data points sorted. Sorting order depends on whether we are
        looking for the maximum or minimum of a function.
    """

    if not isinstance(data, list):
        raise TypeError("Data most be a list")

    # Sort data based on first column
    if sim_params['maximum']:
        data_sorted = np.array(sorted(data, key=lambda x: x[0], reverse=True))
    else:
        data_sorted = np.array(sorted(data, key=lambda x: x[0]))

    best_candidates = []
    fitness = []

    sorted_population = []
    number_best_candidates = sim_params['number_best_candidates']
    for item in data_sorted:
        sorted_population.append(item[1:])
        if len(best_candidates) < number_best_candidates:
            best_candidates.append(item[1:])
            fitness.append(item[0])

    logging.debug("{} parents have successfully been selected".format(number_best_candidates))
    logging.debug(pformat(best_candidates))
    return best_candidates, fitness, sorted_population


def get_parents_roulette(data, sim_params):
    """Selects N=number_best_candidates data points from data based on roulette wheel selection.

    Parameters
    ----------
    data : list
        List of the data points (array) from output file.
    sim_params : dict
        Dictionary with the simulation details read from the input file.

    Returns
    -------
    best_candidates : list (arrays)
        Returns list of best_candidates.
    fitness : list
        Returns list with ordered values of the objective (fitness) function for
        the best_candidates.
    sorted_population : list (arrays)
        List of all data points sorted. Sorting order depends on whether we are
        looking for the maximum or minimum of a function.
    """

    if not isinstance(data, list):
        raise TypeError("Data must be a list")

    # Sort data based on first column
    if sim_params['maximum']:
        data_sorted = np.array(sorted(data, key=lambda x: x[0], reverse=True))
    else:
        data_sorted = np.array(sorted(data, key=lambda x: x[0]))
    
    fitness_inv = []
    sorted_population = []
    number_best_candidates = sim_params['number_best_candidates']
    maximum = sim_params['maximum']
    min_fitness = min(x[0] for x in data_sorted)
    max_fitness = max(x[0] for x in data_sorted)
    
    for i, item in enumerate(data_sorted):
        sorted_population.append(item[1:])
        if not maximum:
            if item[0] == 0:
                fitness_inv.append(min_fitness)
            else:
                fitness_inv.append(1/item[0])
        else:
            if item[0] == 0:
                fitness_inv.append(max_fitness)
            else:
                fitness_inv.append(item[0])

    total_fit = np.sum(fitness_inv)
    cumul_selection_prob = []
    
    for i, item in enumerate(fitness_inv):
        if i == 0:
            cumul_selection_prob.append(fitness_inv[i]/total_fit)
        else:
            cumul_selection_prob.append(cumul_selection_prob[i - 1] + fitness_inv[i]/total_fit)

    best_candidates = []
    fitness = []

    while len(best_candidates) < number_best_candidates:
        rand = random.random()
        for i, prob in enumerate(cumul_selection_prob):
            if rand < prob:
                best_candidates.append(data_sorted[i][1:])
                fitness.append(data_sorted[i][0])
                break
    logging.debug("{} parents have successfully been selected".format(number_best_candidates))
    logging.debug(pformat(best_candidates))
    return best_candidates, fitness, sorted_population


def mutate(data, set_param, sim_param, fitness, opt_step):
    """Generates small changes in the data. The mutation probability is
    determined by the fitness of the data point. Parameters in the data points
    are muated randomly. The mutations size of each parameter is determined by
    the parameter scale_factor.

    Parameters:
    ----------
    data : list (arrays)
        List of data points (arrays) to mutate.
    set_param : :obj:`smartstopos.utils.parameters.set_parameters`
        Set parameters to be explored
    sim_param:  dict
        Dictionary with the simulation details read from the input file.
    fitness: list
        Fitness values of data
    opt_step: int
        Current optimization step

    Returns
    -------
    mutated_points : list (arrays)
        Mutated data points.
    """

    number_parameters = len(set_param.parameters.items())
    if 'number_parameters' in sim_param.keys():
        if number_parameters != sim_param['number_parameters']:
            raise ValueError("The number of parameters is inconsistent")

    if 'population_size' in sim_param.keys():
        population_size = sim_param['population_size']
    else:
        population_size = sim_param['number_best_candidates']*number_parameters

    if not isinstance(data, list):
        raise TypeError("Data most be a list")

    # FIXME: flag to avoid to many duplicated
    mutated = True

    random.seed(sim_param['seed'])
    mutated_points = copy.deepcopy(data)
    mutated_points = []    # copy.deepcopy(data)
    proba_mutation = sim_param['proba_mutation']

    if number_parameters == 1:
        while len(mutated_points) < population_size:
            for k, point in enumerate(data):
                param = list(set_param.parameters.values())[0]
                while True:
                    test_mutation = point + param.scale_factor*random.uniform(-1, 1)
                    logging.debug("{} -->{}".format(point, test_mutation))
                    if test_mutation > param.range[0] and test_mutation < param.range[1]:
                        logging.debug("Mutation accepted")
                        if param.data_type == 'discrete':
                            mutated_points.append(np.array(test_mutation, dtype=int))
                        else:
                            mutated_points.append(np.array(test_mutation, dtype=float))
                        break

    elif number_parameters > 1:
        for _ in range(population_size):
            k = random.sample(range(len(data)), 1)[0]
            point = data[k]
            if k in range(len(fitness)):
                if sim_param['maximum']:
                    if fitness[k] >= np.average(fitness):
                        proba_mutation = 0.5  # maybe higher?
                    else:
                        proba_mutation = 0.5*(fitness[k] - np.amin(fitness))/(np.average(fitness) - np.amin(fitness))
                elif not sim_param['maximum']:
                    if fitness[k] <= np.average(fitness):
                        proba_mutation = 0.5  # maybe higher?
                    else:
                        proba_mutation = 0.5*(fitness[k] - np.amin(fitness))/(np.average(fitness) - np.amin(fitness))
            for i, param in enumerate(set_param.parameters.values()):
                if random.random() < proba_mutation:
                    test_mutation = copy.copy(point)
                    while True:
                        test_mutation[i] = point[i] + (param.scale_factor)*random.uniform(-1, 1)
                        # print("{} -->{}".format(point, test_mutation))
                        if test_mutation[i] >= param.range[0] and test_mutation[i] <= param.range[1]:
                            # print ("Mutation accepted")
                            # TODO: check if add float or int?
                            # TODO: if other constraints satisfied?
                            mutated_points.append(test_mutation)
                            break
                else:
                    mutated_points.append(point)
                    mutated = False
                if not mutated:
                    proba_mutation = 1.0
                    mutated = True
    logging.debug("Mutated data points from input data have been created")
    logging.debug("Size mutated points: {}".format(len(mutated_points)))
    logging.debug(pformat(mutated_points))
    return mutated_points


def crossover(data, set_param, sim_param):
    """Swaps parameter values between the data points in data.

    Parameters
    ----------
    data : list (arrays)
        Array with the data points corresponding to the fittest and their
        mutations.
    set_param : :obj:`smartstopos.utils.parameters.set_parameters`
        Set parameters to be explored
    sim_param: dict
        Simulation information read from input file

    Returns
    -------
    crossover_points: list (arrays)
        List with data points after crossover. If no population size defined, it
        creates N=number_best_candidates*number_parameters new points. The new
        points are created by randomly swapping parameters of the data points.
    """
    if not isinstance(data, list):
        raise TypeError("Data must be a list")

    number_parameters = len(set_param.parameters)
    if 'number_parameters' in sim_param.keys():
        if number_parameters != sim_param['number_parameters']:
            raise ValueError("The number of parameters seems inconsistent")

    random.seed(sim_param['seed'])
    crossover_points = copy.deepcopy(data)

    if 'population_size' in sim_param.keys():
        number_of_crossover_children = int(sim_param['proba_crossover'] * sim_param['population_size'])
    else:
        number_of_crossover_children = number_parameters*sim_param['number_best_candidates']

    if number_parameters > 1:
        for i in range(number_of_crossover_children):
            if (len(crossover_points) >= number_of_crossover_children):
                break
            if random.random() < sim_param['proba_crossover']:
                i1, i2 = random.sample(range(len(data)), 2)
                a = data[i1][:].copy()
                b = data[i2][:].copy()
                crossover_location = random.randrange(1, number_parameters)
                a[crossover_location:] = b[crossover_location:]
                crossover_points.append(a)

    # For one parameter, more mutations are added.
    if number_parameters == 1:
        param = list(set_param.parameters.values())[0]
        for k, point in enumerate(data):
            if random.random() < sim_param['proba_crossover']:
                while True:
                    test_mutation = point + param.scale_factor*random.uniform(-1, 1)
                    logging.debug("{} -->{}".format(point, test_mutation))
                    if test_mutation > param.range[0] and test_mutation < param.range[1]:
                        logging.debug("mutation accepted")
                        # if other constraints satisfied?
                        if param.data_type == 'discrete':
                            crossover_points.append(np.array(test_mutation, dtype=int))
                        else:
                            crossover_points.append(np.array(test_mutation, dtype=float))
                        break
    logging.debug("Crossover data points from input data have been created")
    logging.debug("Size crossover points: {}".format(len(crossover_points)))
    logging.debug(pformat(crossover_points))
    return crossover_points


def check_constraints(sim_param, set_param, new_individuals):
    """Verify that all global constraints are satisfied, otherwise remove data points

    Parameters
    ----------
    new_individuals : list
        List of sets of parameters generated from parents through crossover and mutation

    Returns
    -------
    clean_new_individuals : list
        List of sets of parameters after removing the ones that do not satisfy constraints
    """
    clean_new_individuals = evaluate_constraints(sim_param, set_param, new_individuals)
    if len(clean_new_individuals) != len(new_individuals):
        print("Some points did not satisfy the constraints. They have been removed")
    return clean_new_individuals


def replace_population(sorted_data, new_individuals, population_size):
    """Creates the population for the next generation taking individuals generated through crossover and mutation
    and a) 'filling' the rest of the empty spots with the best elements from the
    previous generation, or b) removing some of the elements of the new_individuals.
    Elitism is also implemented, i.e., the best solution from the previous generation is always passed on.
    This can lead to duplicate data point as generations advance.

    Parameters
    ----------
    sorted_data : list
        List of sets of parameters ordered according to the corresponding value of the objective function.
    new_individuals : list
        List of sets of parameters generated from parents through crossover and mutation
    population_size : int
        Desired number of individuals in next generation
    """
    number_of_new_individuals = len(new_individuals)

    if number_of_new_individuals >= population_size:
        new_pop = random.sample(new_individuals, population_size - 1)
        new_pop.append(sorted_data[0])
        logging.debug("New generation of data points has been resized to the population size defined in input")
    elif len(sorted_data) > population_size - number_of_new_individuals:
        sorted_data_clean = random.sample(sorted_data[1:], population_size - number_of_new_individuals - 1)
        sorted_data_clean.append(sorted_data[0])
        new_pop = np.concatenate((sorted_data_clean, new_individuals))
        logging.debug("New generation of data points has been resized to the population size defined in input")
    else:
        new_pop = np.concatenate(sorted_data, new_individuals)
        logging.debug("WARNING: Not enough data points to keep population size.")

    return new_pop


def scale_mutation_sizes(set_param, opt_step, number_steps):
    """Rescales the mutation size based on the variance of the parameters

    Parameters
    ----------
    set_param: dict
        Set of parameters being explored.
    opt_step: int
        Current optimization step
    number_steps
        Total number of optimization steps
    """
    for i, param in enumerate((set_param.parameters.values())):
        init_scale_factor = float(param.scale_factor/float(1.0 - (opt_step - 1.0)/number_steps))
        param.scale_factor = float(init_scale_factor * (1.0 - opt_step/number_steps))

    logging.debug("Mutation size has been rescaled")
    return


def scale_probabilities(sim_param, factor, opt_step):
    """Rescales the probability of mutation and crossover depending on how many
    optimization steps have been performed

    Parameters
    ----------
    sim_param: dict
        Simulation parameters as read from input file
    factor: float
        Rescaling factor
    opt_step: int
        Current optimization step
    """
    sim_param['proba_mutation'] = 1 - sim_param['proba_mutation']/factor*(opt_step/sim_param['opt_steps'])
    sim_param['proba_crossover'] = 1 - sim_param['proba_crossover']/factor*(opt_step/sim_param['opt_steps'])


def genetic_algorithm(data, set_param, sim_param, opt_step):
    """Creates a new generation of data points based on genetic algorithms.

    Parameters
    ----------
    data : list
        Data from output file
    set_param : smartstopos object
        Set parameters to be explored
    sim_param : dict
        Simulation information, parameters for algorithm
    opt_step : int
        The current generation being generated (step number)

    Returns
    -------
    new_generation : list of arrays
        New set of data points to be explored. Each data point is a set of
        parameters values.
    """
    if not isinstance(data, list):
        raise TypeError("Data is not a list")

    # choose parents according to specified scheme
    if 'roulette' in sim_param.keys() and sim_param['roulette']:
        parents, fitness, sorted_data = get_parents_roulette(data, sim_param)
    else:
        parents, fitness, sorted_data = get_parents(data, sim_param)

    # scale the mutation size. Size gets smaller with simulation step
    if opt_step > 1:
        scale_mutation_sizes(set_param, opt_step, sim_param['opt_steps'])
    # Either first mutation or first crossover
    if 'c' in sim_param.keys() and sim_param["c"]:
        crossover_parents = crossover(parents, set_param, sim_param)
        mutated_parents = mutate(crossover_parents, set_param, sim_param, fitness, opt_step)
        clean_mutated_parents = check_constraints(sim_param, set_param, mutated_parents)
        new_generation = replace_population(sorted_data, clean_mutated_parents, sim_param['population_size'])
        # new_generation = mutated_parents
        logging.debug("New generation, length {}".format(len(new_generation)))
        logging.debug(pformat(new_generation))

    if 'm' in sim_param.keys() and sim_param["m"]:
        mutated_parents = mutate(parents, set_param, sim_param, fitness, opt_step)
        crossover_parents = crossover(mutated_parents, set_param, sim_param)
        clean_crossover_parents = check_constraints(sim_param, set_param, crossover_parents)
        new_generation = replace_population(sorted_data, clean_crossover_parents, sim_param['population_size'])
        logging.debug("New generation, length {}".format(len(new_generation)))
        logging.debug(pformat(new_generation))
    # Check for duplicates
    unique_data = [list(x) for x in set(tuple(x) for x in new_generation)]
    # Remove duplicates? Uncomment line below
    # new_generation = unique_data
    logging.debug("New generation created. In total {} new data points to explore".format(len(new_generation)))
    logging.debug("Number of duplicated data points at step {}: {}"
                  .format(opt_step, len(new_generation)-len(unique_data)))
    # print (new_generation)
    return new_generation
