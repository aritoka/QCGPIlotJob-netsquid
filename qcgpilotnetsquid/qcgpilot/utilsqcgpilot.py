import glob
import os
import random
import logging
import shutil
import subprocess

def copyfiles(workdir, projectdir, filesneeded):
    """ Copy files needed for the projectdir to the workdir
    Parameters
    ----------
        workdir: string
            Directory where the simulations are run (inside the optimization
            steps directories)
        projectdir: string
            Directory where the project is run
        filesneeded: list
            Files and direcotries that need to be copied from workdir to
            currentdir in order to run the simulations """

    for f in filesneeded:
        if os.path.isdir(f):
            shutil.copytree(projectdir +"/" + f, workdir +'/'+f)
        #TODO: generalize to any extension?
        if f == "*.py":   
            for p in glob.glob(projectdir+"/"+f):
                shutil.copy(p, workdir)
        else:
            shutil.copy(projectdir +"/" + f, workdir +'/'+f)
            
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
