#!/bin/bash
set -euo pipefail

# ================================================================
# run-train-more.sh
# Fine-tune CodeGPT on mixed dataset: BCB(10% balanced) + Camel
#
# Inputs:
#   ../dataset/train_mix.txt
#   ../dataset/valid_mix.txt
#   ../dataset/test.txt
#   ../dataset/mix/data.jsonl   (loaded via --test_type mix)
#
# Key args:
#   --test_type mix        -> makes run.py load ../dataset/mix/data.jsonl
#   --subsample_ratio 1.0  -> use full mixed data (do NOT subsample again)
# ================================================================

echo ">>> [System Config] Detecting Hardware..."

# Count available GPUs
NUM_GPUS=$(nvidia-smi --query-gpu=name --format=csv,noheader | wc -l)

# Hyperparameters (keep same as your CodeGPT setting)
PER_GPU_BATCH=8
TARGET_GLOBAL_BATCH=64
EPOCHS=2

# Calculate Gradient Accumulation Steps: 64 / (8 * Num_GPUs)
ACCUM_STEPS=$(( TARGET_GLOBAL_BATCH / (PER_GPU_BATCH * NUM_GPUS) ))
[ "$ACCUM_STEPS" -lt 1 ] && ACCUM_STEPS=1

echo "    - GPUs Detected : $NUM_GPUS"
echo "    - Per-GPU Batch : $PER_GPU_BATCH"
echo "    - Accumulation  : $ACCUM_STEPS"
echo "    - Global Batch  : $TARGET_GLOBAL_BATCH"
echo "    - Epochs        : $EPOCHS"

# Launch command (single vs multi GPU)
LAUNCH_CMD="accelerate launch"
[ "$NUM_GPUS" -gt 1 ] && LAUNCH_CMD="$LAUNCH_CMD --multi_gpu --num_processes $NUM_GPUS"

# Output directory
OUTDIR="./saved_models_mix"
mkdir -p "$OUTDIR"

echo ">>> [Start] Fine-tuning on mixed dataset (BCB10% + Camel)"
echo "    - Output Dir : $OUTDIR"
echo "    - Log File   : $OUTDIR/train_mix.log"
echo "    - Dataset    : ../dataset/train_mix.txt / ../dataset/valid_mix.txt"
echo "    - Mapping    : ../dataset/mix/data.jsonl (via --test_type mix)"

$LAUNCH_CMD run.py \
  --output_dir="$OUTDIR/" \
  --subsample_ratio 1.0 \
  --model_type=gpt2 \
  --config_name=microsoft/CodeGPT-small-java-adaptedGPT2 \
  --model_name_or_path=microsoft/CodeGPT-small-java-adaptedGPT2 \
  --tokenizer_name=microsoft/CodeGPT-small-java-adaptedGPT2 \
  --test_type mix \
  --do_train \
  --do_test \
  --train_data_file=../dataset/train_mix.txt \
  --eval_data_file=../dataset/valid_mix.txt \
  --test_data_file=../dataset/test.txt \
  --block_size 400 \
  --train_batch_size "$PER_GPU_BATCH" \
  --gradient_accumulation_steps "$ACCUM_STEPS" \
  --eval_batch_size 32 \
  --epoch "$EPOCHS" \
  --learning_rate 5e-5 \
  --max_grad_norm 1.0 \
  --evaluate_during_training \
  --save_steps 500 \
  --logging_steps 100 \
  --save_total_limit 2 \
  --overwrite_output_dir \
  --seed 3 2>&1 | tee "$OUTDIR/train_mix.log"