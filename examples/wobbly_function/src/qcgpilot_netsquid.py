import json
import os
import shutil
from argparse import ArgumentParser
from datetime import datetime
from qcg.pilotjob.api.manager import LocalManager
from qcg.pilotjob.api.job import Jobs
from qcgpilotnetsquid.utils.readinput import read_input_json
from qcgpilotnetsquid.utils.createpoints import create_datapoints
from qcgpilotnetsquid.utils.copyfiles import copyfiles

def commandline(j, point, step, general):
    """Create command line to run jobs
    Parameters
    ----------
        j: int
            Counter value of datapoints to be explore in optimization step
        point: array
            Array with variable values to be explored
        step: int
            Optimization step
        general: dict
            Information read form json input file
    Return
    ------
        instruction: string
            Command line instruction to be added to job
    
    """
    instruction = [str(general["program"])]
    variables = general['parametersarguments'] 
    if general['configfile'] and general['paramfile']:
        paramfilename = general['paramfile']
        paramfilename_new = general['paramfile'] + str(j)
        configfilename = general['configfile']
        os.copy(paramfilename, paramfilename_new)
        for i,v in enumerate(variables):
#            subprocess.call(["sed", "-i",'s/{}:/poiny[i]/g', paramfilename_new])
            old = str(v)
            new = old + ":" + point[i]
            subprocess.call(['sed -i "s/' + old + '/' + new + '/g"' + paramfilename_new],shell=True)
        subprocess.call(['sed -i "s/' + parmfilename + '/' + paramfilename_new + '/g"' + configfilename],shell=True)
        instruction.append("--paramfile " + str(general['configfile']) + "--configfile " + str(general[paramfile]))

    elif general['commandline']:
        for i, lineargs in enumerate(general['parametersarguments'].split()):
            instruction.append("--" + str(lineargs))
            instruction.append(point[i])
    else:
        TypeError ("Please specifcy how to run your program")

    if 'outputfile' in general:
        instruction.append(" --output")
        instruction.append(str(general['outputfile']))
    if 'otherarguments' in general:
        key, value = general["otherarguments"].split()
        instruction.append("--" + key)
        instruction.append(value+str(step)+str(j))
    if 'inputfile' in general:
        instruction = program + "--" + str(general['inputfile'])
    return instruction

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


def optimization_workflow(sim_param, set_param, data, manager, algorithm, optsteps, optdir,
                         csvfiledir, projectdir, restartcsv=None,
                         restart=False, flag=''):
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
    general = data['general']
    system = data['system']
    if general["csvfileprefix"]:
        csvprefix = general['csvfileprefix'] + "_"
    else:
        csvprefix = "csv_output_"
    
    print(algorithm) 
    # Optimization workflow
    for step in range(0, optsteps):
        print("-----------------------------")
        print("step : {}".format(step))
        jobs = Jobs()
        names = []
        workdir = optdir + "opt_step_" + str(step) +"/"
        print(workdir)
        if not os.path.exists(workdir):
            os.mkdir(workdir)
        # copy files needed from projectdir to workdir
        copyfiles(workdir, projectdir, general["files_needed"])

        csvfile = csvprefix + str(step) + ".csv"
        print("Creating data points to run...")
        datapoints = create_datapoints(sim_param, set_param, 
                                       algorithm, csvfiledir, csvprefix, 
                                       optdir, step, restartcsv, restart=restart)
        print("done")

        for j, point in enumerate(datapoints):
            names.append(general['name_project'] + "_" + str(step) + "_" + str(j) + flag)
            instruction = commandline(j, point, step, general)
            
            if step == 0:
                jobs.add(
                        name = general['name_project']+"_"+ str(step)+ "_" + str(j) + flag,
                        exec = 'python3',
                        args = instruction,
                        numCores = system['ncores'],
                        wd = workdir
                )
            
            else: 
                jobs.add(
                        name=general['name_project']+"_"+ str(step)+ "_" + str(j) + flag,
                        exec='python3',
                        args=instruction,
                        numCores=system['ncores'],
                        wd=workdir,
                        after=[analysis]
                )
        jobs.add(
            name=general['name_project']+'_analysis_'+str(step) + flag,
            exec='python3',
            args=[general['analysis_program'],"--step", step],
            numCores=system['ncores'],
            after=names,
            wd=workdir
        )
        print("Submitting jobs...")
        job_ids = manager.submit(jobs)
        #print('submited jobs: ', str(job_ids))
        #job_status = manager.status(job_ids)
        #print('job status: ', job_status)
        manager.wait4(job_ids)
        print("jobs finished")
        job_status = manager.status(job_ids)
        print('job status: ', job_status)
        if csvfiledir is not None:
            shutil.copyfile(workdir + csvfile, csvfiledir + csvfile)

        analysis = general['name_project'] + '_analysis_' + str(step) + flag
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

    f = open(inputfile, 'r')
    infoinput = json.load(f)
    # general['run'] is almost the same as sim_param.
    # TODO: change all to work with general instead of sim_param?
    # The weird set_param construction probably can be subsitute by something
    # simple, just a directory infoinput['parameters']..lots of refactoring
    # needed
    sim_param, set_param = read_input_json(inputfile)
    general = infoinput['general']

    
    print("Creating directory structure...")
    # TODO: add case of single parameter run? Basically the same as optsteps = 1
    # singledir = projectdir/output/name-project/single/

    # optdir = projectdir/output/name-project/optimization/
    optdir = directorystructureNLBlueprint(projectdir, general)
    print("done")
    
    # Initialize QCGpilot manager
    print("Initializing qcgpilot...")
    manager = LocalManager()
    print("done")
    
    # First optimization
    # define and create, if needed, directory containing csvfiles
    if general['csvfiledir'] is not None:
        csvfiledir = general['csvfiledir']
        csvfiledir = optdir + csvfiledir + "/" 
        if not os.path.exists(csvfiledir):
            os.mkdir(csvfiledir)

    optsteps = int(general['run']['type']['steps'])
    algorithm = general['run']['type']['optimization']
    print(algorithm)

    optimization_workflow(sim_param, set_param, infoinput, manager, algorithm,
optsteps, optdir, csvfiledir, projectdir)
    print("optimization workflow finished")
    

    # Second optimization
    print("\n\n---------------------------")
    print("---------------------------")
    print("Starting second optimization")
    localoptdir = optdir + "/localoptimization/"
    isExist = os.path.exists(localoptdir)
    if not isExist:
        os.mkdir(localoptdir)
    if general['csvfiledir'] is not None:
        csvfiledir = general['csvfiledir']
        csvfiledir = localoptdir + csvfiledir + "/" 
        if not os.path.exists(csvfiledir):
            os.mkdir(csvfiledir)
    localoptsteps = int(general['run']['type']['localopt']['steps'])
    algorithm = general['run']['type']['localopt']['algorithm']
    restartcsv = optdir + "opt_step_" + str(optsteps - 1) + "/csv_output_" + str(optsteps - 1) + ".csv"
    optimization_workflow(sim_param, set_param, infoinput, manager, algorithm, localoptsteps, localoptdir, 
                         csvfiledir, projectdir, restartcsv=restartcsv,
                         restart=True, flag="local")
    
    manager.cleanup()
    manager.finish()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('--inputfile', required=False, default="input_file.json", type=str,
                        help='File with the input information about the simulation and parameters')
    parser.add_argument('--projectdir', required=False, default=os.getcwd(), type=str,
                        help='Main directory where simualtiosn are launched from')
    args = parser.parse_args()
    main(args.inputfile, args.projectdir)
