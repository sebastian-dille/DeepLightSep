#!/bin/bash
BATCH -J TrainingMLProject     # Name that will show up in squeue
SBATCH --gres=gpu:1         # Request 4 GPU "generic resource"
SBATCH --time=2-00:00       # Max job time is 3 hours
SBATCH --output=%N-%j.out   # Terminal output to file named (hostname)-(jobid).out
SBATCH --partition=long     # long partition (allows up to 7 days runtime)
SBATCH -w cs-venus-02       # Run it on venus-02 node
# The SBATCH directives above set options similarly to command line arguments to srun
# Run this script with: sbatch my_experiment.sh
# The job will appear on squeue and output will be written to the current directory
# You can do tail -f <output_filename> to track the job.
# You can kill the job using scancel <job_id> where you can find the <job_id> from squeue

# Your experiment setup logic here
conda activate DeepLightSep
hostname
echo $CUDA_AVAILABLE_DEVICES
python train.py --dataroot /project/aksoy-lab/datasets/MultiIllumWild/ --model threelayers_color --continue_train --name FirstTrain --lrA 0.0001 --lrB 0.0001 --niter 100 --niter_decay 100  --display_id -1 --gpu_ids 0
