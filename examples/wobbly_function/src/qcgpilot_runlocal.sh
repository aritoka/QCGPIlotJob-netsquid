#!/usr/bin/env bash

input_file=input_file.json
projectdir=${PWD}

# QCGPilot Job installed on Snellius!
module load 2021
module load QCG-PilotJob/0.12.3-foss-2021a

# otherwise source venv with qcgpilot package
# e.g source /home/arianat/qcgpilot_env/bin/activate

# path to qcgpilot_netsquid
export PYTHONPATH=$PYTHONPATH:/home/arianat/qcgpilot_netsquid/

# run code
python3 qcgpilot_netsquid.py --inputfile $input_file  --projectdir $projectdir

