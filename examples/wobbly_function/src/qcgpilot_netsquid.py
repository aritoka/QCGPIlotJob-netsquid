import json
import os
import shutil
from argparse import ArgumentParser
from qcg.pilotjob.api.manager import LocalManager
from qcg.pilotjob.api.job import Jobs
from qcgpilotnetsquid.utils.createpoints import create_datapoints
from qcgpilotnetsquid.utils.dirstructureNLBlueprint import create_dir_structure
from qcgpilotnetsquid.utils.parameters import dict_to_setparameters
from qcgpilotnetsquid.utils.parameters import SetParameters
from qcgpilotnetsquid.utils.qcgpilot import copyfiles
from qcgpilotnetsquid.utils.qcgpilot import commandline_qcgpilot


class InputParams:
    """ Default is a single run"""
    def __init__(self, data, projectdir):
        self.run = data['run']
        self.system = data['system']
        self.general = data['general']
        self.param = SetParameters()
        self.algorithm = "None"
        self.optsteps = 0
        self.rundir = ""
        self.csvfiledir = ""
        if "qcgpilot_netsquid_dir" in self.system.keys():
            self.projectdir = self.system["qcgpilot_netsquid_dir"] + "src/"
        else:
            self.projectdir = projectdir
        self.restartcsv = None
        self.restart = False
        self.flag = ""
        self.check()
        self.createSetParam(data)

    def createSetParam(self, data):
        self.param = dict_to_setparameters(data['parameters']) #IMPROVE
 
    def check(self):
        if self.run["type"] not in ("single", "optimization"):
            ValueError("no run type defined")
        if self.run["type"] == "optimization":
            if self.run["maximum"] not in self.run.keys():
                ValueError("no maximum defined")
        if self.general["runmode"] not in ("commandline", "files"):
            ValueError("no run mode defined")
        if self.general["runmode"] == "files":
            if "configfile" and "paramfile" not in simparameters.general.keys():
                ValueError("Configfile or paramfile not defined")
   
    def define_dircsvfiles(self):
        if self.general['csvfiledir'] is not None:
            self.csvfiledir = self.rundir + self.general['csvfiledir'] + "/" 
            if not os.path.exists(self.csvfiledir):
                os.mkdir(self.csvfiledir)
    
    def print_info(self):
        print("Project dir: {}".format(self.projectdir))
        print("Run mode = {}".format(self.general["runmode"]))
        print("Run type = {}".format(self.run["type"]))
        print("Sweep parameters info:")
        self.param.list_parameters()

    def init_algorithm_param(self, opt=0):
        algorithm = self.run["algorithm"][opt]
        self.optsteps = int(algorithm['steps'])
        self.algorithm = algorithm['name']
        # call check of algorithm???
        if algorithm["restart"] == "true":
            self.restart = True



def optimization_workflow(simparameters, manager, opt):
    """
    Define optimization workflow

    Parameters
    ----------
        simparameters: class InputParam()
            simulation parameters read from input file
        manager: LocalManager 
            object qcgpilot
        opt: int
            optimization number 
    """
    if simparameters.general["csvfileprefix"]:
        csvprefix = simparameters.general['csvfileprefix'] + "_"
    else:
        csvprefix = "csv_output_"
    
    # Optimization workflow
    for step in range(0, simparameters.optsteps):
        print("-----------------------------")
        print("step : {}".format(step))
        jobs = Jobs()
        names = []
        workdir = simparameters.rundir + "opt_step_" + str(step) +"/"
        if not os.path.exists(workdir):
            os.mkdir(workdir)

        # copy files needed from projectdir to workdir
        copyfiles(workdir, simparameters.projectdir, simparameters.general["files_needed"])
        csvfile = csvprefix + str(step) + ".csv"

        print("Creating data points to run...")
        datapoints = create_datapoints(simparameters, csvprefix, step, opt, restart=simparameters.restart)
        print("done")

        for j, point in enumerate(datapoints):
            names.append(simparameters.general['name_project'] + "_" + str(step) + "_" +
str(j) + simparameters.flag)
            instruction = commandline_qcgpilot(j, point, step, simparameters.general)
            
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
                        name=simparameters.general['name_project']+"_"+
                                str(step)+ "_" + str(j) + simparameters.flag,
                        exec='python3',
                        args=instruction,
                        numCores=simparameters.system['ncores'],
                        wd=workdir,
                        after=[analysis]
                )
        jobs.add(
            name=simparameters.general['name_project']+'_analysis_'+str(step) + simparameters.flag,
            exec='python3',
            args=[simparameters.general['analysis_program'],"--step", step],
            numCores=simparameters.system['ncores'],
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
        if simparameters.csvfiledir is not None:
            shutil.copyfile(workdir + csvfile, simparameters.csvfiledir + csvfile)

        analysis = simparameters.general['name_project'] + '_analysis_' + str(step) + simparameters.flag
        del names


def main(inputfile, projectdir):
    """ Workflow for several optimizations
    Parameters
    ----------
        inputfile: str
            Input file name
        projectdir: str
            Path where to run simulations (/src). Defauls is current directory
    """
    if os.path.isfile(projectdir + "/" + inputfile):
        f = open(inputfile, 'r')
        data = json.load(f)
    else:
        ValueError("No valid input file")

    simparameters = InputParams(data, projectdir)
    simparameters.print_info()

    print("\nInitializing qcgpilot...")
    manager = LocalManager()
    
    # Loop over optimizations 
    for i, item in enumerate(simparameters.run["algorithm"]):
        simparameters.init_algorithm_param(opt=i)
        print("\n---------------------------")
        print("Starting optimization {}; algorithm {}, steps {}, restart {}".format(i,
              item["name"], item["steps"], item["restart"]))
        runname = "optimization" + str(i)
        simparameters.rundir = create_dir_structure(simparameters, runname)
        simparameters.define_dircsvfiles()
        if simparameters.restart:
            simparameters.restartcsv = previousrundir + "opt_step_" + str(simparameters.optsteps - 1) + "/"
        
        # Flag needed for qcgpilot naming issues
        simparameters.flag = str(i)

        optimization_workflow(simparameters, manager, i)
       
        print("optimization workflow {} finished".format(i))
        print("results in {}".format(simparameters.rundir))
        previousrundir = simparameters.rundir
    print("\nSimulation finished")
    manager.cleanup()
    manager.finish()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('--inputfile', required=True, default="input_file.json", type=str,
                        help='File with the input information about the simulation and parameters')
    parser.add_argument('--projectdir', required=False, default=os.getcwd(), type=str,
                        help='Main directory where simualtions are launched from')
    args = parser.parse_args()

    # default project dir is current directory, this is overwritten by
    # arg.projectdir and further by the inputfile
    projectdir = os.getcwd()
    
    if args.projectdir:
        projectdir = args.projectdir 
    
    main(args.inputfile, projectdir)
