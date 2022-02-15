#!/usr/bin/env bash
#SBATCH --nodes=2
#SBATCH --time=00:10:00
#SBATCH --job-name=qcg-test
#SBATCH --partition=short

# QCGPilot Job installed on Snellius!
module load 2021
module load QCG-PilotJob/0.12.3-foss-2021a
# otherwise source venv with qcgpilot package
# e.g source /home/arianat/qcgpilot_env/bin/activate

# path to qcgpilot_netsquid
export PYTHONPATH=$PYTHONPATH:/home/arianat/qcgpilot_netsquid/

input_file=input_file.json
maindir=/home/arianat/qcgpilot_netsquid/example/wobbly_function/

tmp_dir="$(mktemp -d -p /scratch-shared)"
mkdir $tmp_dir
cp -r $maindir/src $tmp_dir
cd $tmp_dir/src/
echo "Simulation will be run in : $tmp_dir"
python3 qcgpilot_netsquid.py --inputfile $input_file  --projectdir $tmp_dir/src/
cp -r $tmp_dir/output $maindir
rm -r $tmp_dir
