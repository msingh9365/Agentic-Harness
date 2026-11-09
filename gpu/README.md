# Running the experiments on your college GPU server

This folder runs the two-level Nebula experiments on a remote GPU and sends the
results back through GitHub, so they can be read and added to REPORT.md.

You type commands in a terminal on your laptop, connected to the server with
`ssh`. Lines starting with `#` below are explanations, not commands.

## What you need

* An account on the GPU server that you can reach with `ssh`.
* About **15 GB of free disk space** in your home (or project) folder.
* A **GitHub token**, so the server can download this (private) repository and
  upload the results. To create one:
  GitHub → your picture → **Settings** → **Developer settings** →
  **Personal access tokens** → **Fine-grained tokens** → **Generate new token**.
  Under *Repository access* choose **Only select repositories** →
  `msingh9365/Agentic-Harness`. Under *Permissions → Repository permissions*,
  set **Contents** to **Read and write**. Copy the token. When `git` asks for
  a password, paste the token (your normal password does not work).
  **Never paste the token into a chat or a file in the repository.**

## Step 1: connect and get the code

```bash
ssh your_username@your.gpu.server            # use the address your college gave you
git clone -b nebula-length-study https://github.com/msingh9365/Agentic-Harness.git
# username: msingh9365    password: the token from above
cd Agentic-Harness
```

## Step 2: one-time setup (30–90 minutes, mostly downloading)

```bash
bash gpu/setup.sh
```

This installs the Python packages, downloads Nebula and the 5.5 GB
Speakeasy dataset next to the repository, runs the tests and prepares the data.
At the end it prints `SETUP DONE`. It also prints whether a GPU is visible.
On many clusters the login machine has no GPU; that is fine for setup.

If it says no Python 3.10/3.11 was found, and the server has `conda`:

```bash
conda create -y -n nebula python=3.11 && conda activate nebula
PYTHON=python bash gpu/setup.sh
```

If your lab does not allow long jobs on the login machine, ask them how to run
a CPU job, or run setup inside the SLURM job (see step 4).

## Step 3: a 5-minute test on the GPU

This uses a tiny part of the data. It only checks that everything works; the
numbers mean nothing.

```bash
# if the server uses SLURM, first get an interactive GPU session, e.g.:
#   srun --gres=gpu:1 --time=00:30:00 --pty bash
EXTRA="--limit 300" SEEDS=0 EPOCHS=2 WARMUP=1 OUT_DIR=../gputest bash gpu/run_experiments.sh
```

You should see `device=cuda` in the logs (`../gputest/logs/`) and a summary
table at the end. Then delete the test: `rm -rf ../gputest`.

## Step 4: the real run (a few hours, depending on the GPU)

It runs 3 settings × 3 seeds = 9 trainings (see "What is run" below).

**If your server uses SLURM** (you submit jobs with `sbatch`):

```bash
# first open gpu/slurm_job.sh and set the partition/account your lab uses
sbatch gpu/slurm_job.sh
squeue -u $USER                       # is it waiting (PD) or running (R)?
tail -f results/gpu/slurm-*.out       # watch it; press Ctrl+C to stop watching (the job keeps running)
```

**If there is no job system** (you just run programs on the GPU machine), use
`tmux` so the run continues after you disconnect:

```bash
tmux new -s nebula                    # opens a session that survives disconnects
bash gpu/run_experiments.sh
# press Ctrl+B, then D, to leave it running. Later: ssh in again and run
tmux attach -t nebula
```

If the run stops for any reason (time limit, disconnect), start the same
command again. Finished trainings are skipped.

## Step 5: send the results back

When it prints `ALL DONE`:

```bash
git add results/gpu
git commit -m "GPU results"
git push origin HEAD:gpu-results      # username + token, as in step 1
```

Then just say **"results pushed"** in the chat. They are on the `gpu-results`
branch and can be read from there: the summary, every run's test scores, the
logs, and `env.txt` (which GPU and versions were used). Model weights (`*.pt`)
are not uploaded.

**If `git push` is not possible from the server:** pack the results, copy them
to your laptop, and upload them on GitHub in the browser:

```bash
# on the server
tar czf gpu_results.tgz results/gpu
# on your laptop (a new terminal, not the ssh one)
scp your_username@your.gpu.server:Agentic-Harness/gpu_results.tgz .
```

Then on github.com open the repository → **Add file** → **Upload files**, drop
`gpu_results.tgz`, choose **Create a new branch** named `gpu-results`, and
commit.

## What is run

All runs fine-tune both levels with the improved training recipe:

| setting | chunks read | how level 2 sums up the chunks |
|---|---|---|
| `k1_cls` | 1 (same input as Nebula) | [CLS] vector |
| `k8_cls` | up to 8 | [CLS] vector |
| `k8_max` | up to 8 | the most suspicious chunk (max) |

The recipe:
1. **Warm-up (epochs 1–2):** Nebula (level 1) is frozen; only level 2 learns.
2. **Fine-tuning (epochs 3–10):** Nebula learns with a small learning rate
   (0.00003), and level 2 with a larger one (0.001).
3. The best epoch is chosen by **validation loss** (validation AUC is ~0.999
   for every model on this data, so it cannot choose).
4. Each setting runs with **3 seeds** (0, 1, 2).

The summary reports mean ± spread over seeds, compares 8 chunks with 1 chunk
seed by seed, and compares everything with the released Nebula on the same
17,402 test samples.

Change the plan with settings in front of the command, e.g.
`SEEDS="0 1 2 3 4" EPOCHS=15 bash gpu/run_experiments.sh`.

## If something goes wrong

| problem | what to do |
|---|---|
| `No GPU visible` | You are on a machine without a GPU. Use `sbatch` or `srun --gres=gpu:1 ...` (SLURM), or ask your lab which machine has the GPU. |
| `CUDA out of memory` | Add `EXTRA="--batch-size 32"` in front of the command. |
| `CUDA available: False` although the machine has a GPU | The installed torch does not match the server's CUDA. Install the right build from <https://pytorch.org/get-started/locally/>, then run step 2 again. |
| a training fails | Its log is in `results/gpu/logs/`. Push the results anyway (step 5); the logs show what went wrong. |
