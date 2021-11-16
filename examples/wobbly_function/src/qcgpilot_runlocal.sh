#!/usr/bin/env bash

input_file=input_file.json
workdir=/home/arianat/test/smart-stopos/examples/qcgpilot

# source venve qcgpilot package
# source /home/arianat/qcgpilot_env/bin/activate

# path to smartstopos
export PYTHONPATH=$PYTHONPATH:/home/arianat/test/smart-stopos

# run code
python3 qcgpilot_netsquid.py --inputfile $input_file  --projectdir $workdir/src/

