#!/bin/bash
# For servers that use the SLURM job scheduler (you submit jobs instead of running them directly).
# Submit from the repository root:   sbatch gpu/slurm_job.sh
# Check it:                          squeue -u $USER
# Watch the output:                  tail -f results/gpu/slurm-<jobid>.out
# The lines below starting with #SBATCH are settings; ask your lab which partition/account to use
# and edit them (lines starting with "##" are switched off).
#SBATCH --job-name=hier-nebula
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=24:00:00
#SBATCH --output=results/gpu/slurm-%j.out
##SBATCH --partition=gpu
##SBATCH --account=your_account

mkdir -p results/gpu
nvidia-smi || true
bash gpu/run_experiments.sh
