set -euo pipefail

ts=$(date +%Y%m%d_%H%M%S)

python run.py \
  --output_dir=./saved_models \
  --train_data_file=../dataset/train.txt \
  --model_type=gpt2 \
  --model_name_or_path=./saved_models \
  --tokenizer_name=microsoft/CodeGPT-small-java-adaptedGPT2 \
  --do_test \
  --test_data_file=../dataset/test.txt \
  --block_size 400 \
  --eval_batch_size 32 \
  2>&1 | tee -a ./saved_models/console.log

# ===== 테스트 끝난 후 결과 정리 =====

out=./saved_models/test_runs/test_$ts
mkdir -p "$out"

# 결과물 이동
mv ./saved_models/predictions.txt "$out/" 2>/dev/null || true
mv ./saved_models/console.log     "$out/" 2>/dev/null || true

# 메타 정보
{
  echo "DATE: $(date)"
  echo "TEST_DIR: $out"
  echo "MODEL_DIR: $(readlink -f ./saved_models)"
  echo "GIT: $(git rev-parse HEAD 2>/dev/null || echo N/A)"
} > "$out/meta.log"

# saved_models/
# ├── checkpoint-best-f1/
# ├── train_full.log
# ├── test_runs/
# │   ├── test_20260205_013500/
# │   │   ├── predictions.txt
# │   │   ├── console.log
# │   │   └── meta.log
# │   └── test_20260205_021012/
# │       ├── predictions.txt
# │       ├── console.log
# │       └── meta.log

# train script.
# $LAUNCH_CMD run.py \
#     --output_dir=./saved_models_size_400/ \
#     --model_type=gpt2 \
#     --config_name=microsoft/CodeGPT-small-java-adaptedGPT2 \
#     --model_name_or_path=microsoft/CodeGPT-small-java-adaptedGPT2 \
#     --tokenizer_name=microsoft/CodeGPT-small-java-adaptedGPT2 \
#     --do_train \
#     --do_test \
#     --train_data_file=../dataset/train.txt \
#     --eval_data_file=../dataset/valid.txt \
#     --test_data_file=../dataset/test.txt \
#     --block_size 400 \
#     --train_batch_size $PER_GPU_BATCH \
#     --gradient_accumulation_steps $ACCUM_STEPS \
#     --eval_batch_size 32 \
#     --epoch 2 \
#     --learning_rate 5e-5 \
#     --max_grad_norm 1.0 \
#     --evaluate_during_training \
#     --save_steps 500 \
#     --logging_steps 100 \
#     --save_total_limit 2 \
#     --overwrite_output_dir \
#     --seed 3 2>&1 | tee ./saved_models_size_400/train_full.log