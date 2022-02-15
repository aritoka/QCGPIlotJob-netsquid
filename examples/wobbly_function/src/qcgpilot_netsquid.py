import json
import os
import shutil
from argparse import ArgumentParser
from qcg.pilotjob.api.manager import LocalManager
from qcg.pilotjob.api.job import Jobs
from qcgpilotnetsquid.utils.createpoints import create_datapoints
from qcgpilotnetsquid.utils.copyfiles import copyfiles
from qcgpilotnetsquid.utils.dirstructureNLBlueprint import create_dir_structure
from qcgpilotnetsquid.utils.qcgpilot import copyfiles
from qcgpilotnetsquid.utils.qcgpilot import commandline_qcgpilot
from qcgpilotnetsquid.utils.inputparams import InputParamsOpt

def optimization_workflow(simparameters, manager, opt):
    """
    Define optimization workflow

    Parameters
    ----------
        simparameters: class InputParam()
            Simulation parameters read from input file
        manager: qcgpilot object LocalManager() 
            Manger of the qcgpilto workflow
        opt: int
            optimization number
    """
    # Optimization workflow
    for step in range(0, simparameters.optsteps):
        print("step : {}\n--------".format(step))
        jobs = Jobs()
        names = []
        workdir = simparameters.rundir + "opt_step_" + str(step) +"/"
        if not os.path.exists(workdir):
            os.mkdir(workdir)

        # copy files needed to run simulations from projectdir to workdir
        print("Copying files needed from projectdir to workdir...")
        copyfiles(workdir, simparameters)
        print("Creating data points to run...")
        datapoints = create_datapoints(simparameters, step, opt)
        
        print("Adding jobs to submit...")
        # Add one job per datapoint in optimization
        for j, point in enumerate(datapoints):
            names.append(simparameters.general['name_project'] + "_" + str(step) + "_" +
                        str(j) + simparameters.flag)

            instruction = commandline_qcgpilot(j, point, step, simparameters.general)
            #print("run arguments qcgpilot: {}".format(instruction))
            if step == 0:
                jobs.add(
                        name = simparameters.general['name_project']+"_"+ str(step)+ "_" +
                               str(j) + simparameters.flag,
                        exec = 'python3',
                        args = instruction,
                        numCores = simparameters.system['ncores'],
                        wd = workdir
                )

            else:
                jobs.add(
                        name = simparameters.general['name_project']+"_"+
                               str(step)+ "_" + str(j) + simparameters.flag,
                        exec = 'python3',
                        args = instruction,
                        numCores = simparameters.system['ncores'],
                        wd = workdir,
                        after = [analysis]
                )

        # Add analysis job
        jobs.add(
            name = simparameters.general['name_project'] + '_analysis_' +
                   str(step) + simparameters.flag,
            exec = 'python3',
            args = [simparameters.general['analysis_program'],"--step", step],
            numCores = simparameters.system['ncores'],
            after = names,
            wd = workdir
        )

        print("Submitting jobs...")
        job_ids = manager.submit(jobs)
        manager.wait4(job_ids)

        # if csvfiledir define, copy opt_step csv to dir
        csvfile = simparameters.general["csvfileprefix"] + "_" + str(step) + ".csv"
        if step < simparameters.optsteps:
            if simparameters.csvfiledir is not None:
                shutil.copyfile(workdir + csvfile, simparameters.csvfiledir + csvfile)

        analysis = simparameters.general['name_project'] + '_analysis_' + str(step) + simparameters.flag
        print ("Jobs finished\n")
        del names


def main(inputfile, projectdir):
    """ Workflow to run several optimizations after each other NLBlueprint
    Parameters
    ----------
        inputfile: str
            Input file name
        projectdir: str
            Path to src/ of simulations. Default is current directory
    """
    if os.path.isfile(projectdir + "/" + inputfile):
        f = open(inputfile, 'r')
        data = json.load(f)
    else:
        ValueError("No valid input file")

    simparameters = InputParamsOpt(data, projectdir)
    simparameters.print_info()

    print("\nInitializing qcgpilot...")
    manager = LocalManager()

    # Loop over optimizations 
    for i, item in enumerate(simparameters.run["algorithm"]):
        simparameters.init_opt_algorithm(item)
        simparameters.print_info_algorithm()
        runname = "optimization" + str(i)
        rundir = create_dir_structure(simparameters, runname)
        simparameters.setRunDir(rundir) 
        print("rundir: {}".format(simparameters.rundir))
        simparameters.setCsvFileDir()
        print("csvfiledir: {}".format(simparameters.csvfiledir))
        print("optsteps: {}".format(simparameters.optsteps))
            
        if simparameters.restart:
            restartfile = previousrundir + "opt_step_" + str(previousrunsteps - 1) + "/" + simparameters.general["csvfileprefix"] + "_" + str(previousrunsteps - 1 ) + ".csv"
            simparameters.setRestartCsvFile(restartfile)
            print("restartcsvfile: {}".format(simparameters.restartcsvfile))

        # Flag needed for qcgpilot naming issues
        simparameters.flag = str(i)

        optimization_workflow(simparameters, manager, i)
    
        print("optimization workflow {} finished".format(i))
        print("results in {}".format(simparameters.rundir))
        previousrundir = simparameters.rundir
        previousrunsteps = simparameters.optsteps
    print("\nSimulation finished")
    manager.cleanup()
    manager.finish()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('--inputfile', required=True, default="input_file.json", type=str,
                        help='File with the input information about the simulation and parameters')
    parser.add_argument('--projectdir', required=False, type=str, default=os.getcwd(),
                        help='Main directory where simualtions are launch from (path/src/')
    args = parser.parse_args()

    # default projectdir is current directory, this is overwritten by
    # arg.projectdir and further by inputfile 
    if args.projectdir:
        projectdir = args.projectdir 
    
    main(args.inputfile, projectdir)
