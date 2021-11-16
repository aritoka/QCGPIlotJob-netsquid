#!/usr/bin/env bash
#SBATCH --nodes=2
#SBATCH --time=00:10:00
#SBATCH --job-name=qcg-test
#SBATCH --partition=short

function read_input {
    input_file=$1
    if [ $# -eq 0  ]; then
        input_file=input_file.json #(default name)
    fi
    configfile="$(awk '/"configfile":/ {print $2}' < $input_file)"
    paramfile="$(awk '/"paramfile":/ {print $2}' < $input_file)"
    sstoposdir="$(awk '/"sstoposdir":/{print $2}' < $input_file)"
    if [ -z $sstoposdir ]; then
        echo "WARNING: no sstoposdir defined; looking for repo in system" 1>&2
        sstoposdir=$(find ~/ -name ".git" | grep "smart-stopos\/" | sed "s/.git//")
        if [[ -z $sstoposdir ]]; then
            echo "No smart-stopos repository found" 1>&2
            exit 1
        fi
        # TODO: add error for when more than one repo found! Pipe it through wc?
        echo "Repo found at $sstoposdir"
    fi
}


function create_directorystructure {
    echo "Creating directory structure"
    cd $workdir
    echo $workdir
    sourcedir=$workdir/src
    outputdir=$workdir/output
    time_stamp=$(date +'%Y-%m-%d_%H.%M')
    folder_name=$name\_$time_stamp
    
    mkdir -p $outputdir
    cd $sourcedir
    time_stamp=$(date +'%Y-%m-%d_%H.%M')
    folder_name=$name\_$time_stamp
    #folder_name=$name
    tmp_dir="$(mktemp -d -p /scratch-shared)"
    tmp_rundir=$tmp_dir/$folder_name
    mkdir $tmp_rundir
    run_dir=$tmp_dir/$folder_name/$run_type
    mkdir $run_dir
    echo "Simulation will be run in : $run_dir"
}

#----------------------main---------------------------
input_file=input_file.json
name="WobblyFunction"
run_type="optimization"
workdir=/home/arianat/test/smart-stopos/examples/qcgpilot
read_input

# source venve qcgpilot package
source /home/arianat/QCGpilotjob/qcg_env/bin/activate

# path to smartstopos
export PYTHONPATH=$PYTHONPATH:/home/arianat/test/smart-stopos

create_directorystructure

# run code
cd $workdir/src
cp $input_file *.py $run_dir
cd $run_dir
python qcgpilot.py --input_file $input_file
cp -r $tmp_dir/$folder_name $workdir/output/
rm -r $tmp_dir

