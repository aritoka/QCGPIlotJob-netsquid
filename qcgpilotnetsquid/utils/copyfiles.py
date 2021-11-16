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

