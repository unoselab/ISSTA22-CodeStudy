mkdir -p ./saved_models/

# ==============================================================================
#  OPTIMIZED TRAINING SCRIPT FOR DUAL RTX 6000 ADA (96GB VRAM)
# ==============================================================================
#
#  USAGE INSTRUCTIONS (Run in Background):
#  -----------------------------------------------------------------------------
#  To run this script in the background and save a log file with the current
#  timestamp (format: mmdd_hhmm), run the following command:
#
#      nohup bash run_optimized.sh > log_$(date +%m%d_%H%M).txt 2>&1 &
#
#  To monitor the training progress in real-time:
#
#      tail -f log_*.txt
#  -----------------------------------------------------------------------------
#
#  COMPARISON: ORIGINAL vs. OPTIMIZED
#  ---------------------------------------------------------------------------------------------------------
#  | Feature          | Original (run.sh)      | Optimized (this script)    | Impact on Research           |
#  |------------------|------------------------|----------------------------|------------------------------|
#  | Launcher         | python run.py          | accelerate launch          | Enables Distributed Data     |
#  |                  | (Single GPU/Process)   | (Multi-GPU DDP)            | Parallel (True Parallelism)  |
#  |------------------|------------------------|----------------------------|------------------------------|
#  | GPU Usage        | ~50% of 1 card         | ~100% of BOTH cards        | Massive speedup by using     |
#  |                  |                        |                            | all 96GB of available VRAM   |
#  |------------------|------------------------|----------------------------|------------------------------|
#  | Context Window   | 400 tokens             | 1024 tokens (Max)          | CRITICAL for Clone Detection:|
#  | (--block_size)   |                        |                            | See full function bodies     |
#  |------------------|------------------------|----------------------------|------------------------------|
#  | Batch Size       | 16 (Global)            | 32 Per GPU (64 Global)     | More stable gradients and    |
#  |                  |                        |                            | smoother convergence         |
#  |------------------|------------------------|----------------------------|------------------------------|
#  | Training Duration| 2 Epochs               | 5 Epochs                   | Ensures convergence with     |
#  | (--epoch)        |                        |                            | the larger batch size        |
#  ---------------------------------------------------------------------------------------------------------

# OPTIMIZATION NOTES:
# 1. Launcher: Uses 'accelerate launch' for Distributed Data Parallel (DDP) on 2 GPUs.
# 2. Context Window (--block_size): Set to 1024 (Model Max) to capture full function bodies for clone detection; your 48GB VRAM can easily handle this.
# 3. Batch Size (--train_batch_size): Set to 32 per GPU (64 global) to maximize Tensor Core usage on RTX 6000 Ada.
# 4. Epochs (--epoch): Increased to 5 to ensure convergence since the larger batch size results in fewer weight updates per epoch.

accelerate launch --multi_gpu --num_processes 2 --mixed_precision=fp16 run.py \
    --output_dir=./saved_models/ \
    --model_type=gpt2 \
    --config_name=microsoft/CodeGPT-small-java-adaptedGPT2 \
    --model_name_or_path=microsoft/CodeGPT-small-java-adaptedGPT2 \
    --tokenizer_name=microsoft/CodeGPT-small-java-adaptedGPT2 \
    --do_train \
    --do_test \
    --train_data_file=../dataset/train.txt \
    --eval_data_file=../dataset/valid.txt \
    --test_data_file=../dataset/test.txt \
    --block_size 1024 \
    --train_batch_size 16 \
    --gradient_accumulation_steps 2 \
    --eval_batch_size 32 \
    --epoch 5 \
    --learning_rate 2e-5 \
    --max_grad_norm 1.0 \
    --evaluate_during_training \
    --seed 3 2>&1 | tee ./saved_models/train_optimized.log