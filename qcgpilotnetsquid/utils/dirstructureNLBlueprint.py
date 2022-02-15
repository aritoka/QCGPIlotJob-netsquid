import os
from datetime import datetime

def create_dir_structure(simparameters, runname):
    """ Creates the directory structure agreed in the NLblueprint
    Parameters
    ----------
    simparameters: class InputParam()
       Infromation read from input file 
    runname: str
        run type: single or optimization
    Returns
    -------
    rundir: str
        Main optimization dir projectdir/output/name-project/runname
or projectdir/output/name-project/single
    """
    projectdir = simparameters.projectdir
    general = simparameters.general
    outputdir = projectdir.split("/src")[0] + "/output"
    
    if not os.path.exists(outputdir):
        os.mkdir(outputdir)

    dateTimeObj = datetime.now()
    timestampStr = dateTimeObj.strftime("%Y-%b-%d_%H:%M:%S")

    # uncomment timestamp in actual production
    nameprojectdir = outputdir + "/" + general['name_project'] #+ "_" + timestampStr + "/"

    if not os.path.exists(nameprojectdir):
        os.mkdir(nameprojectdir)

    rundir = nameprojectdir + "/" + runname + "/" 

    if not os.path.exists(rundir):
        os.mkdir(rundir)

    return rundir

