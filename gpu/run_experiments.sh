#!/bin/bash
# Run the experiment sweep on the GPU and summarise it. From the repository root:
#     bash gpu/run_experiments.sh
# Every run writes results/gpu/<run>_seed<N>/ (result.json, test_scores.csv) and a log in
# results/gpu/logs/. Finished runs are skipped, so if the job stops you can just start it again.
#
# Optional settings (environment variables), e.g.  SEEDS="0 1 2 3 4" EPOCHS=12 bash gpu/run_experiments.sh
#   SEEDS    random seeds              (default "0 1 2")
#   EPOCHS   total epochs per run      (default 10, of which WARMUP are warm-up)
#   WARMUP   warm-up epochs, Nebula frozen (default 2)
#   RUNS     which runs (default "k1_cls k8_cls k8_max")
#   ALLOW_CPU=1  run even if no GPU is visible (very slow; for testing only)
#   OUT_DIR  where results go (default results/gpu)
#   EXTRA    extra arguments for every run, e.g. EXTRA="--limit 300" for a quick test
set -uo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"
source ../nebula-venv/bin/activate

SEEDS="${SEEDS:-0 1 2}"
EPOCHS="${EPOCHS:-10}"
WARMUP="${WARMUP:-2}"
RUNS="${RUNS:-k1_cls k8_cls k8_max}"
OUT=${OUT_DIR:-results/gpu}
mkdir -p "$OUT/logs"

if ! python -c "import torch,sys; sys.exit(0 if torch.cuda.is_available() else 1)"; then
  if [ "${ALLOW_CPU:-0}" != 1 ]; then
    echo "No GPU visible (torch.cuda.is_available() is False). On a SLURM cluster, submit with sbatch gpu/slurm_job.sh."
    exit 1
  fi
fi

# record the conditions of this sweep (sent back with the results)
{
  echo "date: $(date -u)"; echo "host: $(hostname)"; echo "git commit: $(git rev-parse HEAD)"
  python -c "import torch; print('torch', torch.__version__, 'cuda', torch.version.cuda, '|', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'cpu')"
  command -v nvidia-smi >/dev/null && nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv
  echo "SEEDS=$SEEDS EPOCHS=$EPOCHS WARMUP=$WARMUP RUNS=$RUNS"
} > "$OUT/env.txt" 2>&1
cat "$OUT/env.txt"

# The improved training recipe (see hier_nebula/README.md):
#   warm-up epochs with Nebula frozen, then fine-tune with a small learning rate for Nebula
#   (3e-5) and a larger one for level 2 (1e-3); best epoch chosen by validation loss.
COMMON="--data ../hier_data/speakeasy --mode finetune --epochs $EPOCHS --warmup-epochs $WARMUP \
        --lr 1e-3 --lr-level1 3e-5 --batch-size 64 --workers 4 --select val_loss ${EXTRA:-}"
declare -A ARGS=(
  [k1_cls]="--max-chunks 1 --pool cls"
  [k8_cls]="--max-chunks 8 --pool cls"
  [k8_max]="--max-chunks 8 --pool max"
)

for seed in $SEEDS; do
  for run in $RUNS; do
    dir="$OUT/${run}_seed${seed}"
    if [ -f "$dir/result.json" ]; then echo "skip $dir (done)"; continue; fi
    echo "=== $(date -u +%H:%M) start $run seed $seed"
    python -m hier_nebula.train train $COMMON ${ARGS[$run]} --seed "$seed" --out "$dir" \
      > "$OUT/logs/${run}_seed${seed}.log" 2>&1 \
      && grep "^TEST" "$OUT/logs/${run}_seed${seed}.log" \
      || echo "!!! $run seed $seed FAILED, see $OUT/logs/${run}_seed${seed}.log"
  done
done

python -m gpu.summarize_gpu --data ../hier_data/speakeasy --results "$OUT"
echo
echo "ALL DONE. To send the results back:"
echo "  git add results/gpu && git commit -m 'GPU results' && git push origin HEAD:gpu-results"
