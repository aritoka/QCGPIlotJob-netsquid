import os
from qcgpilotnetsquid.utils.parameters import SetParameters
from qcgpilotnetsquid.utils.parameters import dict_to_setparameters

class InputParams:
    """ Input parameters needed to run a nlblueprint workflow with qcgpilot
job"""
    def __init__(self, data, projectdir):
        def create_set_parameters(self, paramdata):
            return dict_to_setparameters(paramdata)
        
        def set_csv_file_prefix(self, csvprefix=None):
            prefix = "csv_output_"
            if "csvfileprefix" in self.general.keys():
                prefix = self.general['csvfileprefix'] + "_"
            if csvprefix:
                prefix = csvprefix
            
            return prefix

        def set_files_needed(self, filesneeded=None):
            if filesneeded:
                files = filesneeded
            if "files_needed" in self.general.keys():
                files = self.general["files_needed"]
            return files
        
        def set_project_dir(self, projectdir=None):
            if "qcgpilot_netsquid_workdir" in self.system.keys():
                pdir = self.system["qcgpilot_netsquid_workdir"] + "src/"
            if projectdir:
                pdir = projectdir
            return pdir

        self.run = data['run']
        self.system = data['system']
        self.general = data['general']
        self.param = create_set_parameters(self, data["parameters"])
        self.projectdir = set_project_dir(self)
        self.csvprefix = set_csv_file_prefix(self)
        self.filesneeded = set_files_needed(self)
        self.flag = ""
        self.rundir = ""
        self.restartcsvfile = None
        self.restart = False
        self.csvfiledir = None
        self.check()
        
        
    def setCsvFileDir(self, csvfiledir=None):
        if csvfiledir is None:
            if self.general['csvfiledir'] is not None:
                csvfiledir = self.rundir + self.general['csvfiledir'] + "/" 
                if not os.path.exists(csvfiledir):
                    os.mkdir(csvfiledir)
        else:
            if not os.path.exists(csvfiledir):
                os.mkdir(csvfiledir)
        self.csvfiledir = csvfiledir
    
    def setRestartCsvFile(self, restartfile):
        self.restartcsvfile = restartfile
    
    def setRunDir(self, rundir):
        self.rundir = rundir

    def check(self):
        #system
        #run
        #general
        #param
        #flag
        #rundir?
        if self.run["type"] not in ("single", "optimization"):
            ValueError("no run type defined")
        if self.run["type"] == "optimization":
            if self.run["maximum"] not in self.run.keys():
                ValueError("no maximum defined")
        if self.general["runmode"] not in ("commandline", "files"):
            ValueError("no run mode defined")
        if self.general["runmode"] == "files":
            if "configfile" and "paramfile" not in self.general.keys():
                ValueError("Configfile or paramfile not defined")
            else: 
                self.filesneeded.append(self.general["configfile"])
                self.filesneeded.append(self.general["paramfile"])
   
    
    def print_info(self):
        print("Project dir: {}".format(self.projectdir))
        print("Run mode = {}".format(self.general["runmode"]))
        print("Run type = {}".format(self.run["type"]))
        print("Sweep parameters info:")
        print("files needed: {}".format(self.filesneeded))
        self.param.list_parameters()



class InputParamsOpt(InputParams):
    """ Input parameters needed to run a nlblueprint optimization workflow"""
    def __init__(self, data, projectdir):
        InputParams.__init__(self, data, projectdir)
        self.algorithm = "GA"
        self.optsteps = 1
    
    def init_opt_algorithm(self, opt):
        self.optsteps = int(opt["steps"])
        self.algorithm = opt["name"]
        if opt["restart"] == "true":
            self.restart = True

    def print_info_algorithm(self):
        print("\n---------------------------")
        print("Starting optimization\nalgorithm: {},\nsteps: {},\nrestart: {}".format(
              self.algorithm, self.optsteps, self.restart))



class InputParamsSingle(InputParams):
    """ Input parameters needed to run a nlblueprint single run workflow"""
    def __init__(self, data, projectdir):
        InputParams.__init__(self, data, projectdir)

