Here is the improved Markdown version of your file. I have organized it with clear code blocks, syntax highlighting, and structured sections to make it professional and readable.

---

# Fine-tuning with BCB (10%) + Camel Mix

**Date:** 2026-02-06

**Scope:** CodeGPT (first), then CodeBERT (next) using the same mixed dataset.

**Goal:** Improve cross-project generalization by fine-tuning on a mixed dataset comprising:

- **BCB (BigCloneBench):** 10% subset (balanced labels).
- **Camel:** NiCad post-processed pairs (Target domain).

This README documents the **full end-to-end process**, including verification steps, commands, and observed results.

---

## 0. Directory & Files Overview

### Working Directory

`Clone-Detection-BigCloneBench/codegpt/` (Used for CodeGPT mixing & training)

### Dataset Directory Structure

```text
../dataset/
├── train.txt
├── valid.txt
├── test.txt
├── data.jsonl
├── train_10percent.txt          # Generated in Step 1
├── valid_10percent.txt          # Generated in Step 1
├── train_mix.txt                # Final Mixed Training Set
├── valid_mix.txt                # Final Mixed Validation Set
└── mix/                         # Mixed Artifacts Folder
    ├── data.jsonl               # Combined Source Code Mapping
    ├── train_bcb.pref.txt
    ├── valid_bcb.pref.txt
    ├── train_more.pref.txt
    └── valid_more.pref.txt

```

### More-data (Camel) Location

```text
../../../detect_clones/NiCad/post_process/data/java/camel/
├── train.txt
├── valid.txt
└── data.jsonl

```

---

## 1. Why “Mix” Requires Data Processing

`run.py` loads clone pairs (`train.txt`, `valid.txt`) containing columns: `id1 \t id2 \t label`.
It resolves each `id` into source code using a single mapping file (`data.jsonl`).

> **Critical Constraint:**
> If a pair contains an `id` not present in the mapping file, `run.py` skips it:
> `if url1 not in url_to_code or url2 not in url_to_code: continue`

**Therefore, mixing datasets safely requires:**

1. **Mixed Pair Files:** A single text file containing pairs from both BCB and Camel.
2. **Combined Mapping File:** A `data.jsonl` that contains code for **both** sources (handling potential ID collisions).

---

## 2. Overall Pipeline

We run the mix pipeline in **two steps**:

1. **Step 1 — Sample 10% from BCB (Balanced):**
   Generate a reproducible 10% subset of BCB pairs first to control training size and ensure stability.
2. **Step 2 — Mix BCB (10%) with Camel:**

- Create `train_mix.txt` (BCB 10% + Camel Train).
- Create `valid_mix.txt` (BCB 10% + Camel Valid).
- Create `mix/data.jsonl` (Concatenated BCB + Camel JSONL with ID prefixes).

---

## 3. Step 1 — Create BCB 10% Dataset

**Script:** `1_sample_data.py`

### Command

```bash
python 1_sample_data.py --seed 3 --mode balanced

```

### Observed Output

```text
[IN ] train.txt: total=901028 label0=450166 label1=450862
[OUT] train_10percent.txt: total=90102 label0=45051 label1=45051

[IN ] valid.txt: total=415416 label0=361577 label1=53839
[OUT] valid_10percent.txt: total=41540 label0=20770 label1=20770

```

### ✅ Verification Results

- BCB train 10% size = **90,102**
- BCB valid 10% size = **41,540**
- Both are label-balanced (0/1 = 50:50).
- Sampling is deterministic (`seed=3`).

---

## 4. Step 2 — Mix BCB (10%) + Camel

**Script:** `2_mix_data.py`

### Command

```bash
python 2_mix_data.py \
  --train_data_file_bcb ../dataset/train_10percent.txt \
  --valid_data_file_bcb ../dataset/valid_10percent.txt \
  --train_data_file_more ../../../detect_clones/NiCad/post_process/data/java/camel/train.txt \
  --valid_data_file_more ../../../detect_clones/NiCad/post_process/data/java/camel/valid.txt \
  --bcb_jsonl ../dataset/data.jsonl \
  --more_jsonl ../../../detect_clones/NiCad/post_process/data/java/camel/data.jsonl \
  --seed 3

```

### Process Details

1. **Prefix IDs:** To avoid collisions and clarify source.

- BCB IDs `bcb_` prefix.
- Camel IDs `camel_` prefix.

2. **Create Prefixed Pair Files:** Saves to `../dataset/mix/*.pref.txt`.
3. **Combine Code Mappings:** Concatenates JSONLs into `../dataset/mix/data.jsonl`.
4. **Merge & Shuffle:** Final outputs `train_mix.txt` and `valid_mix.txt`.

---

## 5. Observed Output (Execution Log)

**Command:** `./run-mix-data.sh`

```text
[OK] prefixed pairs: ../dataset/train_10percent.txt -> ../dataset/mix/train_bcb.pref.txt (lines=90102)
[OK] prefixed pairs: ../dataset/valid_10percent.txt -> ../dataset/mix/valid_bcb.pref.txt (lines=41540)
[OK] prefixed pairs: .../camel/train.txt -> ../dataset/mix/train_more.pref.txt (lines=4068)
[OK] prefixed pairs: .../camel/valid.txt -> ../dataset/mix/valid_more.pref.txt (lines=2034)

[OK] appended jsonl: ../dataset/data.jsonl (+9126) with prefix=bcb_
[OK] appended jsonl: .../camel/data.jsonl (+2739) with prefix=camel_

[OK] merged+shuffled: ../dataset/train_mix.txt (total_lines=94170)
[OK] merged+shuffled: ../dataset/valid_mix.txt (total_lines=43574)

```

### ✅ Verification Results

- **Train Total:** 90,102 (BCB) + 4,068 (Camel) = **94,170**
- **Valid Total:** 41,540 (BCB) + 2,034 (Camel) = **43,574**
- **JSONL Total:** 9,126 + 2,739 = **11,865** functions.

---

## 6. File-Level Verification

### 6.1 File Existence & Line Counts

```bash
ls -lh ../dataset/train_mix.txt ../dataset/valid_mix.txt ../dataset/mix/data.jsonl
wc -l ../dataset/train_mix.txt ../dataset/valid_mix.txt ../dataset/mix/data.jsonl

```

**Result:** ✅ Lines match the calculations in Section 5.

### 6.2 Prefix Validation in Pair Files

```bash
# Check if both prefixes exist in the shuffled training file
grep -m 3 "^bcb_" ../dataset/train_mix.txt
grep -m 3 "^camel_" ../dataset/train_mix.txt

```

**Result:** ✅ Both `bcb_` and `camel_` entries appear in `train_mix.txt`.

### 6.3 Prefix Validation in `mix/data.jsonl`

```bash
grep -m 1 '"idx": "bcb_' ../dataset/mix/data.jsonl
grep -m 1 '"idx": "camel_' ../dataset/mix/data.jsonl

```

**Result:** ✅ Both namespaces exist in the combined JSONL file.

### 6.4 Critical Lookup Test (No Missing IDs)

_Validates that every ID in the pair file exists in the JSONL mapping._

```python
import json, random
from pathlib import Path

# Load mixed pairs
pairs = Path("../dataset/train_mix.txt").read_text().splitlines()
random.seed(3)
sample = random.sample(pairs, 20)

# Load keys from mixed JSONL
jsonl = Path("../dataset/mix/data.jsonl")
keys = set()
for line in jsonl.open():
    js = json.loads(line)
    keys.add(js["idx"])

# Verify
miss = 0
for ln in sample:
    a, b, y = ln.split("\t")
    if a not in keys or b not in keys:
        miss += 1
        print("MISSING:", a, b, y)
print("checked:", len(sample), "missing:", miss)

```

**Observed Result:** `checked: 20 missing: 0`
✅ **Passed.** This ensures `run.py` will not drop data during training.

---

## 7. Training: Fine-tuning CodeGPT on Mixed Dataset

**Key Requirement:**
In this codebase, the mapping file is loaded from `<dataset_dir>/{test_type}/data.jsonl`.
Since our mapping is in `../dataset/mix/data.jsonl`, we **must** set:

- `--test_type mix`
- `--train_data_file ../dataset/train_mix.txt`
- `--eval_data_file ../dataset/valid_mix.txt`

### Training Command

```bash
accelerate launch run.py \
  --output_dir=./saved_models_mix/ \
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
  --train_batch_size 8 \
  --gradient_accumulation_steps 4 \
  --eval_batch_size 32 \
  --epoch 2 \
  --learning_rate 5e-5 \
  --max_grad_norm 1.0 \
  --evaluate_during_training \
  --save_steps 500 \
  --logging_steps 100 \
  --save_total_limit 2 \
  --overwrite_output_dir \
  --seed 3 2>&1 | tee ./saved_models_mix/train.log

```

---

## 8. Next Step: CodeBERT

After CodeGPT training is complete, the **same mixed dataset artifacts** will be reused for CodeBERT fine-tuning:

- Use `../dataset/train_mix.txt`
- Use `../dataset/valid_mix.txt`
- Set `--test_type mix` (to load `../dataset/mix/data.jsonl`)

---

## Appendix: Quick Copy-Paste Commands

### A.1 Mix Pipeline

```bash
# 1) Sample BCB 10% (balanced)
python 1_sample_data.py --seed 3 --mode balanced

# 2) Mix BCB(10%) + Camel
python 2_mix_data.py \
  --train_data_file_bcb ../dataset/train_10percent.txt \
  --valid_data_file_bcb ../dataset/valid_10percent.txt \
  --train_data_file_more ../../../detect_clones/NiCad/post_process/data/java/camel/train.txt \
  --valid_data_file_more ../../../detect_clones/NiCad/post_process/data/java/camel/valid.txt \
  --bcb_jsonl ../dataset/data.jsonl \
  --more_jsonl ../../../detect_clones/NiCad/post_process/data/java/camel/data.jsonl \
  --seed 3

```

### A.2 Verification

```bash
# Counts
wc -l ../dataset/train_mix.txt ../dataset/valid_mix.txt ../dataset/mix/data.jsonl

# Prefix Check
grep -m 3 "^bcb_" ../dataset/train_mix.txt
grep -m 3 "^camel_" ../dataset/train_mix.txt

```
