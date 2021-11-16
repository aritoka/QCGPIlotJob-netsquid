#!/usr/bin/env bash

input_file=input_file.json
projectdir=${PWD}

# source venve qcgpilot package
# source /home/arianat/qcgpilot_env/bin/activate

# path to smartstopos
export PYTHONPATH=$PYTHONPATH:${PWD}/../../..

# run code
python3 qcgpilot_netsquid.py --inputfile $input_file  --projectdir $projectdir

