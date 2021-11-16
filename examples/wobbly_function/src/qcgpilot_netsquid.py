import json
import os
import shutil
from argparse import ArgumentParser
from datetime import datetime
from qcg.pilotjob.api.manager import LocalManager
from qcg.pilotjob.api.job import Jobs
from qcgpilotnetsquid.utils.readinput import read_input_json
from qcgpilotnetsquid.utils.createpoints import create_datapoints
from qcgpilotnetsquid.qcgpilot.utilsqcgpilot import copyfiles
from qcgpilotnetsquid.qcgpilot.utilsqcgpilot import commandline

from qcgpilotnetsquid.utils.parameters import SetParameters
from qcg.pilotjob.api.manager import LocalManager


class optParams:
    sim_param = {}
    set_param = SetParameters()
    data = {}
    manager = LocalManager()
    algorithm = "GA"
    optsteps = 0
    optdir = ""
    csvfiledir = ""
    projectdir = os.getcwd()
    restartcsv = None
    restart = False
    flag = ""


def define_dir_for_csvfiles(general, optdir):
    """
    Define and create, if needed, directory containing csvfiles
    Parameters
    ----------
    general: ???
    optdir: string
            oprimization directory /output/optimization/
    Returns
    -------
        csvfiledir: str
            Directory for the csv files
    """
    if general['csvfiledir'] is not None:
        csvfiledir = general['csvfiledir']
        csvfiledir = optdir + csvfiledir + "/" 
        if not os.path.exists(csvfiledir):
            os.mkdir(csvfiledir)

    return csvfiledir


def directorystructureNLBlueprint(projectdir, general):
    """ Creates the directory structure agreed in the NLbluprint
    Parameters
    ----------
        projectdir: str
            Project directory
        general: dict
            General infromation read from input file 
    Returns
    -------
        optdir: str
            Main optimization dir /output/optimization
    """
    outputdir = projectdir.split("/src")[0] + "/output"
    if not os.path.exists(outputdir):
        os.mkdir(outputdir)
    dateTimeObj = datetime.now()
    timestampStr = dateTimeObj.strftime("%Y-%b-%d_%H:%M:%S")
    # uncomment timestamp in actual production
    nameprojectdir = outputdir + "/" + general['name_project'] #+ "_" + timestampStr + "/"
    if not os.path.exists(nameprojectdir):
        os.mkdir(nameprojectdir)
    optdir = nameprojectdir + "/optimization/"
    if not os.path.exists(optdir):
        os.mkdir(optdir)
    return optdir


def optimization_workflow(parameters):
    """
    Define optimization workflow

    Parameters
    ----------
        input_file: string
            name of input file with simulation information
        data: dict
            Information about the simulation read from input file
        manager: qcgpilot object
            QCGPilot manager
        algorithm: string
            Optimization algorithm to use
        optsteps: int
            optimization steps to be performed
        optdir: string
            oprimization directory /output/optimization/
        csvfiledir: string
            Directory where csvfiles with results are place, if None, then they
            are kept in the opt_step_i directory
        projectdir: string 
            directory project 
        restartcsv: string
            In case of a restart, csvfile from which to start
        restart: bool
            True if the optimization should restart from an existing csv file
        flag: string
            Flag needed for qcgpilot unique job naming convention
    """
    #TODO: remove redundant things: eg sim_param is sort of contained in data
    general = parameters.data['general']
    system = parameters.data['system']
    if general["csvfileprefix"]:
        csvprefix = general['csvfileprefix'] + "_"
    else:
        csvprefix = "csv_output_"
    
    print(parameters.algorithm) 
    # Optimization workflow
    for step in range(0, parameters.optsteps):
        print("-----------------------------")
        print("step : {}".format(step))
        jobs = Jobs()
        names = []
        workdir = parameters.optdir + "opt_step_" + str(step) +"/"
        print(workdir)
        if not os.path.exists(workdir):
            os.mkdir(workdir)
        # copy files needed from projectdir to workdir
        copyfiles(workdir, parameters.projectdir, general["files_needed"])

        csvfile = csvprefix + str(step) + ".csv"
        print("Creating data points to run...")
        datapoints = create_datapoints(parameters.sim_param, parameters.set_param, 
                                       parameters.algorithm, parameters.csvfiledir, csvprefix, 
                                       parameters.optdir, step, parameters.restartcsv, 
                                       restart=parameters.restart)
        print("done")

        for j, point in enumerate(datapoints):
            names.append(general['name_project'] + "_" + str(step) + "_" + str(j) + parameters.flag)
            instruction = commandline(j, point, step, general)
            
            if step == 0:
                jobs.add(
                        name = general['name_project']+"_"+ str(step)+ "_" + str(j) + parameters.flag,
                        exec = 'python3',
                        args = instruction,
                        numCores = system['ncores'],
                        wd = workdir
                )
            
            else: 
                jobs.add(
                        name=general['name_project']+"_"+ str(step)+ "_" + str(j) + parameters.flag,
                        exec='python3',
                        args=instruction,
                        numCores=system['ncores'],
                        wd=workdir,
                        after=[analysis]
                )
        jobs.add(
            name=general['name_project']+'_analysis_'+str(step) + parameters.flag,
            exec='python3',
            args=[general['analysis_program'],"--step", step],
            numCores=system['ncores'],
            after=names,
            wd=workdir
        )
        print("Submitting jobs...")
        job_ids = parameters.manager.submit(jobs)
        #print('submited jobs: ', str(job_ids))
        #job_status = manager.status(job_ids)
        #print('job status: ', job_status)
        parameters.manager.wait4(job_ids)
        print("jobs finished")
        job_status = parameters.manager.status(job_ids)
        print('job status: ', job_status)
        if parameters.csvfiledir is not None:
            shutil.copyfile(workdir + csvfile, parameters.csvfiledir + csvfile)

        analysis = general['name_project'] + '_analysis_' + str(step) + parameters.flag
        del names


def main(inputfile, projectdir):
    """ Workflow for an optimization followed by a local optimization
    Parameters
    ----------
        inputfile: str
            Name input file with information about the simulation
        projectdir: str
            Directory where the inputfile and other needed files are
    """
    
    parameters = optParams()

    parameters.projectdir = projectdir

    f = open(inputfile, 'r')
    parameters.data = json.load(f)
    # general['run'] is almost the same as sim_param.
    # TODO: change all to work with general instead of sim_param?
    # The weird set_param construction probably can be subsitute by something
    # simple, just a directory infoinput['parameters']..lots of refactoring
    # needed
    parameters.sim_param, parameters.set_param = read_input_json(inputfile)
    general = parameters.data['general']

    
    print("Creating directory structure...")
    # TODO: add case of single parameter run? Basically the same as optsteps = 1
    # singledir = projectdir/output/name-project/single/

    # optdir = projectdir/output/name-project/optimization/
    parameters.optdir = directorystructureNLBlueprint(projectdir, general)
    print("done")
    
    # Initialize QCGpilot manager
    print("Initializing qcgpilot...")
    parameters.manager = LocalManager()
    print("done")
    
    # First optimization
    # define and create, if needed, directory containing csvfiles
    csvfiledir = define_dir_for_csvfiles(general, parameters.optdir)

    parameters.optsteps = int(general['run']['type']['steps'])
    parameters.algorithm = general['run']['type']['optimization']
    print(parameters.algorithm)

    parameters.csvfiledir = csvfiledir
    
    optimization_workflow(parameters)
    print("optimization workflow finished")
    
    # Second optimization
    print("\n\n---------------------------")
    print("---------------------------")
    print("Starting second optimization")
    localoptdir = parameters.optdir + "/localoptimization/"
    isExist = os.path.exists(localoptdir)
    if not isExist:
        os.mkdir(localoptdir)
    # define and create, if needed, directory containing csvfiles
    csvfiledir = define_dir_for_csvfiles(general, localoptdir)
    localoptsteps = int(general['run']['type']['localopt']['steps'])
    algorithm = general['run']['type']['localopt']['algorithm']
    restartcsv = parameters.optdir + "opt_step_" + str(parameters.optsteps - 1) \
                                   + "/csv_output_" + str(parameters.optsteps - 1) + ".csv"

    parameters.algorithm = algorithm
    parameters.optsteps = localoptsteps
    parameters.optdir = localoptdir
    parameters.restartcsv = restartcsv
    parameters.restart = True
    parameters.flag = "local"

    optimization_workflow(parameters)
    
    parameters.manager.cleanup()
    parameters.manager.finish()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('--inputfile', required=False, default="input_file.json", type=str,
                        help='File with the input information about the simulation and parameters')
    parser.add_argument('--projectdir', required=False, default=os.getcwd(), type=str,
                        help='Main directory where simualtiosn are launched from')
    args = parser.parse_args()
    main(args.inputfile, args.projectdir)
