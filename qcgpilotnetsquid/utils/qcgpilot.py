import glob
import os
import random
import logging
import shutil
import subprocess


def copyfiles(workdir, simparameters):
    """ Copy files needed for the projectdir to the workdir
    Parameters
    ----------
    workdir: string
        Directory where the simulations are run (inside the optimization
        steps directories)
    simparameters: class InputParam
        Simulation parameters read from input file
    """
    projectdir = simparameters.projectdir
    filesneeded = simparameters.filesneeded

    for f in filesneeded:
        if os.path.isdir(f):
            shutil.copytree(projectdir +"/" + f, workdir +'/'+f)
        #TODO: generalize to any extension?
        if f == "*.py":   
            for p in glob.glob(projectdir+"/"+f):
                shutil.copy(p, workdir)
        else:
            shutil.copy(projectdir +"/" + f, workdir +'/'+f)

def commandline_qcgpilot(j, point, step, general):
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

    if 'inputfile' in general:
        instruction.append(" --inputfile ") 
        instruction.append(str(general['inputfile']))
    if 'outputfile' in general:
        instruction.append(" --output")
        instruction.append(str(general['outputfile']))
    if 'programvariableargs' in general:
        for i, item in enumerate(general["programvariableargs"]):
            key, value = item.split(":")
            instruction.append("--" + key)
            instruction.append(value+str(step)+str(j))
    if 'programfixargs' in general:
        for i, item in enumerate(general["programfixargs"]):
            key, value = item.split(":")
            instruction.append("--" + key)
            instruction.append(value)
    if general["runmode"] == "commandline":
        instruction.extend(commandline_args_qcgpilot(j, point, step, general))
    elif general["runmode"] == "files":
        instruction.extend(commandline_files_qcgpilot(j, point, step, general))
    else:
        TypeError ("Please specify how to run your program")
    return instruction
            
def commandline_args_qcgpilot(j, point, step, general):
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
    variables = general['programsweepargs'] 
    instruction = []
    if general["runmode"] == "commandline":
        for i, item in enumerate(variables):
            instruction.append("--" + str(item))
            instruction.append(point[i])
    return tuple(instruction)

def commandline_files_qcgpilot(j, point, step, general):
    """Create command line using configfile and paramfile to run jobs
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
    variables = general['programsweepargs'] 
    if "paramfile" not in general.keys():
        raise ValueError("No paramfile defined")
    if "configfile" not in general.keys():
        raise ValueError("No configfile defined")
        
    paramfilename = general['paramfile']
    paramfilename_new = general['paramfile'] + "_" + str(j)
    configfilename = general['configfile']
    shutil.copyfile(paramfilename, paramfilename_new)
    for i,v in enumerate(variables):
        line1 = 's/' + str(v) + '\:.*/' + str(v) + ':' +'/g'
        subprocess.call(["sed", "-i ", line1, paramfilename_new])
        old = str(v) + ":" 
        new = str(v) + ": " + str(point[i])
        line2 = 's/' + str(v) + '\:*/' + new + '/g'
        subprocess.call(["sed", "-i ", line2, paramfilename_new])

    line3 = 's/' + paramfilename + '.*/' + paramfilename_new + '/g'
    subprocess.call(["sed", "-i ", line3 , configfilename])
    line = ["--paramfile ", str(paramfilename_new), "--configfile ",
str(general['configfile'])]
    instruction = (line)
    return instruction
