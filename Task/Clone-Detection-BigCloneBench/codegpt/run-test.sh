#!/usr/bin/env bash
set -euo pipefail

# Timestamp used to create a unique archive folder per test run
ts=$(date +%Y%m%d_%H%M%S)

# Run evaluation (test) using the fixed model directory.
# NOTE: run.py expects the fine-tuned checkpoint under:
#   ./saved_models/checkpoint-best-f1/model.bin
# and it writes test outputs (e.g., predictions.txt) into --output_dir.
python run.py \
  --output_dir=./saved_models \
  --train_data_file=../dataset/train.txt \
  --model_type=gpt2 \
  --config_name=microsoft/CodeGPT-small-java-adaptedGPT2 \
  --model_name_or_path=microsoft/CodeGPT-small-java-adaptedGPT2 \
  --tokenizer_name=microsoft/CodeGPT-small-java-adaptedGPT2 \
  --do_test \
  --test_data_file=../dataset/test.txt \
  --block_size 400 \
  --eval_batch_size 32 \
  2>&1 | tee -a ./saved_models/console.log

# ===== After the test finishes, archive outputs into a new directory =====

# Create an archive directory for this test run
out=./saved_models/test_runs/test_$ts
mkdir -p "$out"

# Move per-run outputs into the archive folder (ignore if missing)
# This prevents overwriting predictions/logs on subsequent runs.
mv ./saved_models/predictions.txt "$out/" 2>/dev/null || true
mv ./saved_models/console.log     "$out/" 2>/dev/null || true

# Write lightweight metadata for reproducibility/debugging
{
  echo "DATE: $(date)"
  echo "TEST_DIR: $out"
  echo "MODEL_DIR: $(readlink -f ./saved_models)"
  echo "GIT_COMMIT: $(git rev-parse HEAD 2>/dev/null || echo N/A)"
  echo "CUDA: $(nvidia-smi --query-gpu=name,driver_version --format=csv,noheader 2>/dev/null || echo N/A)"
  echo "PYTHON: $(python -V 2>&1)"
} > "$out/meta.log"