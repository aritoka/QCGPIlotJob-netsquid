QCGPilotJob implementation for NLBlueprint
----------

Description
-----------

Set of tools to run parameters explorations and perform parameters optimization locally and in HPC centers using QCGPilotJob and the specific requirements of the NLBlueprint
QCGPilotJOb repo: https://github.com/vecma-project/QCG-PilotJob
QCGPilotJOb documentation: https://qcg-pilotjob.readthedocs.io/en/develop/


Installation
------------

make build

python3 setup.py build_ext --inplace


Structure 
----------
- qcgpilotnetsquid: 
	- algorithms:
		- ga.py: genetic algorithm
		- random_displacement

	- utils:
	- examples:
	- ext_tests: more complete tests
		- file: test for a workflow usign param.yaml and config.yaml
	- examples: 
	    - wobbly_function

Usage
-----
QCGPilotJob is a tool to run several jobs within a single allocation.
run_program.py --param1 value1 --param2 value2 ... 

Where param1 and param2 are the names of the varaibles to be varied and value1 and value2 some example values of these parameters. 

To run the simulations:

1. Create you running directory eg. MyTest

2. Create a src/ directory inside MyTest/src/

3. Copy the following files from qcgpilotnetsquid/runscripts/ into  MyTest/src

            - qcgpilot_runlocal.sh (if running local)
            - qcgpilot_sbatch.sh (if running on HPC)
            - remove_duplicates.py (WIP only needed on LISA)

4. Add your run_program.py and analysis_program.py to MyTest/src

5. Create a input_file.json to fit your simulation (more info on the input keywords in inputfile_description):

6. Run the script:
- 	./qcgpilot_runlocal: uses qcgpilotjob (can be run in your own computer or interactively in HPC centers)
- 	./qcgpilot_sbatch: uses SLURM + qcgpilotjob (only HPC centers)

Running the script will create a directory MyTest/output where the results will be dumped. For the HPC simualtions be aware that the results are initially stored in the scratch memory. You can see the path to this in the file MyTest/output/running_directory_MyTestName.
You can follow the progress of your simulations there while they are taking place. The whole directory will be copied to your working directory (MyTest/output/) as soon as the simulations are finished.

You can check whether your simulations are running by using:
squeue -u username


You can cancel all the jobs related with a run by using:
cat MyTest/ouput/jobs_id_MyTestName | xargs scancel 


Notes
-----

When performing and optimization, keep in mind that the optimization relies on the existence  of a formated output file. Make sure the final "product" of your analysis_program is a file 
in the correct format: 

    #figure_merit, #p1, #p2, #p3, ....
    figure_merit, p1, p2, p3, ....

	--> separation of columns using ','
	--> First line is for comments
	
	If your output file has a different name than csv_output.csv, 
	make sure you add the --output_file name.csv when running create_opt_pool.py 
	(modify the run_local.sh and/or analysis.job)


Contributors
------------

Ariana Torres Knoop (ariana.torres@surf.nl)
Franciso Silva (F.HortaFerreiradaSilva@tudelft.nl)
David Maier (d.maier@tudelft.nl

