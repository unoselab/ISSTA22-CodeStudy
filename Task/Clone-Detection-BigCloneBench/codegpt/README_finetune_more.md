# Fine-tuning with BCB (10%) + Other-Domain Mix (e.g., Camel)

**Date:** 2026-02-06

**Scope:** CodeGPT (first), then CodeBERT (next) using the same mixed dataset.

**Goal:** Improve **cross-project generalization** by fine-tuning on a mixed dataset comprising:

- **BCB (BigCloneBench):** 10% subset (balanced labels)
- **Other Domain (e.g., Camel):** NiCad post-processed clone pairs

This README documents the **full end-to-end process**, including preprocessing rationale, commands, verification steps, and observed results.

---

## 0. Directory & Files Overview

### Working Directory

`Clone-Detection-BigCloneBench/codegpt/`
(Used for CodeGPT dataset mixing & training)

### Dataset Directory Structure

```text
../dataset/
├── train.txt
├── valid.txt
├── test.txt
├── data.jsonl
├── train_10percent.txt          # Generated in Step 1
├── valid_10percent.txt          # Generated in Step 1
├── train_mix.txt                # Final mixed training set
├── valid_mix.txt                # Final mixed validation set
├── test_mix.txt                 # (Optional) Mixed test set
└── mix/                         # Mixed artifacts
    ├── data.jsonl               # Combined code mapping (BCB + other domain)
    ├── train_bcb.pref.txt
    ├── valid_bcb.pref.txt
    ├── train_other.pref.txt
    ├── valid_other.pref.txt
    └── test_other.pref.txt      # (Optional)
```

### Other-Domain Data Location (Example: Camel)

```text
../../../detect_clones/NiCad/post_process/data/java/camel/
├── train.txt
├── valid.txt
├── test.txt
└── data.jsonl
```

---

## 1. Why Mixing Requires Explicit Preprocessing

`run.py` loads clone pairs (`train.txt`, `valid.txt`, `test.txt`) with format:

```
<id1> \t <id2> \t <label>
```

Each `id` must be resolvable via **a single mapping file** (`data.jsonl`).

> **Critical Constraint in `run.py`:**
> If either ID in a pair is missing from the mapping file, the pair is silently skipped:
>
> ```python
> if url1 not in url_to_code or url2 not in url_to_code:
>     continue
> ```

Therefore, **cross-domain mixing requires**:

1. **Unified pair files** (BCB + other domain)
2. **A combined mapping file** containing code for _all_ IDs
3. **Explicit ID namespaces** to avoid collisions

---

## 2. Overall Pipeline

The pipeline runs in **two deterministic steps**:

### Step 1 — Sample 10% from BCB (Balanced)

- Controls dataset size
- Ensures label balance
- Guarantees reproducibility

### Step 2 — Mix BCB (10%) with Other Domain

- Prefixes IDs to create disjoint namespaces
- Builds a unified `mix/data.jsonl`
- Produces shuffled `train_mix.txt`, `valid_mix.txt`
- (Optionally) produces `test_mix.txt`

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

### ✅ Verification

- Train: **90,102**
- Valid: **41,540**
- Perfect label balance
- Deterministic (`seed=3`)

---

## 4. Step 2 — Mix BCB (10%) + Other Domain (e.g., Camel)

**Script:** `2_mix_data.py`

This script is **domain-agnostic** via `--otherdomain_name`.

### Command (train + valid only)

```bash
python 2_mix_data.py \
  --otherdomain_name camel \
  --train_data_file_bcb ../dataset/train_10percent.txt \
  --valid_data_file_bcb ../dataset/valid_10percent.txt \
  --train_data_file_more ../../../detect_clones/NiCad/post_process/data/java/camel/train.txt \
  --valid_data_file_more ../../../detect_clones/NiCad/post_process/data/java/camel/valid.txt \
  --bcb_jsonl ../dataset/data.jsonl \
  --more_jsonl ../../../detect_clones/NiCad/post_process/data/java/camel/data.jsonl \
  --seed 3
```

### Optional: include test set

```bash
  --test_data_file_otherdomain ../../../detect_clones/NiCad/post_process/data/java/camel/test.txt
```

---

## 5. Mixing Logic (What the Script Does)

1. **Prefix IDs**
    - BCB → `bcb_<id>`
    - Other domain → `<otherdomain_name>_<id>` (e.g., `camel_259_340`)

2. **Create Prefixed Pair Files**
    - Saved under `../dataset/mix/*.pref.txt`

3. **Build Combined Mapping**
    - Concatenate JSONLs into `../dataset/mix/data.jsonl`
    - Apply the same prefixes to `idx`

4. **Merge & Shuffle**
    - Deterministic shuffle using `seed=3`
    - Outputs:
        - `train_mix.txt`
        - `valid_mix.txt`
        - (optional) `test_mix.txt`

---

## 6. Observed Output (Execution Log)

```text
[OK] prefixed pairs: train_10percent.txt -> train_bcb.pref.txt (90102)
[OK] prefixed pairs: valid_10percent.txt -> valid_bcb.pref.txt (41540)
[OK] prefixed pairs: camel/train.txt -> train_other.pref.txt (4068)
[OK] prefixed pairs: camel/valid.txt -> valid_other.pref.txt (2034)

[OK] appended jsonl: data.jsonl (+9126) with prefix=bcb_
[OK] appended jsonl: camel/data.jsonl (+2739) with prefix=camel_

[OK] merged+shuffled: train_mix.txt (94170)
[OK] merged+shuffled: valid_mix.txt (43574)
```

### ✅ Verification

- Train: **94,170**
- Valid: **43,574**
- JSONL entries: **11,865**

---

## 7. Critical Consistency Check (IDs ↔ Mapping)

```python
# Sample-based ID consistency check
checked: 20
missing: 0
```

✅ Confirms **no silent data loss** in `run.py`.

---

## 8. Training CodeGPT on Mixed Dataset

### Required Flags

Because mapping is loaded from `<dataset_dir>/<test_type>/data.jsonl`:

- `--test_type mix`
- `train / eval / test` files must use prefixed IDs

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
  --test_data_file=../dataset/test_mix.txt \
  --block_size 400 \
  --train_batch_size 8 \
  --gradient_accumulation_steps 4 \
  --epoch 2 \
  --learning_rate 5e-5 \
  --seed 3
```

---

## 9. Next Step: CodeBERT

The **same mixed artifacts** are reused:

- `train_mix.txt`
- `valid_mix.txt`
- `test_mix.txt`
- `mix/data.jsonl`

Only the model backend changes.

---

## Appendix: Quick Copy-Paste

```bash
# Step 1
python 1_sample_data.py --seed 3 --mode balanced

# Step 2 (generic other-domain mix)
python 2_mix_data.py \
  --otherdomain_name camel \
  --train_data_file_bcb ../dataset/train_10percent.txt \
  --valid_data_file_bcb ../dataset/valid_10percent.txt \
  --train_data_file_more ../../../detect_clones/NiCad/post_process/data/java/camel/train.txt \
  --valid_data_file_more ../../../detect_clones/NiCad/post_process/data/java/camel/valid.txt \
  --test_data_file_otherdomain ../../../detect_clones/NiCad/post_process/data/java/camel/test.txt \
  --bcb_jsonl ../dataset/data.jsonl \
  --more_jsonl ../../../detect_clones/NiCad/post_process/data/java/camel/data.jsonl \
  --seed 3
```
