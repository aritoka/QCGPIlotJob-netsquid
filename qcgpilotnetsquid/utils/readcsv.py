""" utils"""
import logging
import pandas as pd


def get_subsample_csvfile(data, sim_params, samplesize=10):
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

    subsample = []
    fitness = []

    sorted_population = []
    for item in data_sorted:
        sorted_population.append(item[1:])
        if len(subsample) < samplesize:
            subsample.append(item[1:])
            fitness.append(item[0])

    logging.debug("{} parents have successfully been selected".format(number_best_candidates))
    logging.debug(pformat(best_candidates))
    return subsample, fitness, sorted_population


def readcsvfiles(simparameters, step, backsteps=1,subsample=None):
    """Reads the results obtained in previous steps.
    Parameters
    ----------
    simparameters: class InputParam
        info read from input
    step: int
        Last optimization step
    backsteps: int
        Defines how many previous steps does the optimization algorithms needs
    subsample: bool
        Defines whether we are using only a subsample (eg. best candidates) of
        the data

    Returns
    -------
    csvdata: list of arrays
        Data from previous optimization steps read from csvfiles
    """
    csvfiledir = simparameters.csvfiledir
    csvprefix = simparameters.csvprefix
    rundir = simparameters.rundir
    restartcsv = simparameters.restartcsvfile

    csvdata = []
    csvfiles =[]
    
    if restartcsv is not None and step == 0:
        csvfiles += [restartcsv] 

    else:
        if csvfiledir == None:
            for i in range(0, backsteps):
                temp= rundir + "opt_step_" + str(step - i - 1) + "/" + csvprefix + str(step - i - 1) + ".csv"
                csvfiles += [temp]
        else:
            for i in range(0, backsteps):
                temp = csvfiledir + "/" + csvprefix + str(step - i - 1) + ".csv"
                csvfiles += [temp]
    
    totaldata = [] 

    for f in csvfiles:
        csvdata = list(pd.read_csv(f, engine='python', dtype=float).values)
        if subsample:
            candidates, fitness, sorted_data = get_subsample_csvfiles(csvdata, sim_param)
            csvdata = candidates
        totaldata.insert(0, csvdata)
    return totaldata
