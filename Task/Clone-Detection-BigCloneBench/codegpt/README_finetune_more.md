# README_finetune_more.md — Fine-tuning with BCB(10%) + More-data (Camel) Mix
**Date:** 2026-02-06  
**Scope:** CodeGPT (first), then CodeBERT (next) using the same mixed dataset  
**Goal:** Improve cross-project generalization by fine-tuning on a mixed dataset:
- **BCB (BigCloneBench) 10% subset (balanced labels)**
- **Camel (NiCad post-processed pairs)**

This README documents the **full end-to-end process**, including **verification steps and observed results**.

---

## 0) Directory / Files Overview

### Working directory (example)
- `Clone-Detection-BigCloneBench/codegpt/` (for CodeGPT mixing + training)

### Dataset directory

../dataset/
├── train.txt
├── valid.txt
├── test.txt
├── data.jsonl
├── train_10percent.txt
├── valid_10percent.txt
├── train_mix.txt
├── valid_mix.txt
└── mix/
├── data.jsonl
├── train_bcb.pref.txt
├── valid_bcb.pref.txt
├── train_more.pref.txt
└── valid_more.pref.txt

### More-data (Camel) location

../../../detect_clones/NiCad/post_process/data/java/camel/
├── train.txt
├── valid.txt
└── data.jsonl

---

## 1) Why “Mix” Requires More Than Just Concatenating Pair Files

`run.py` loads clone pairs (`train.txt`, `valid.txt`) with columns:

id1 \t id2 \t label

Then it resolves each `id` into source code using a single mapping file `data.jsonl`:
- `data.jsonl` provides: `{ "idx": <id>, "func": <code> }`

**Important:** If a pair contains an `id` not present in the mapping, it is skipped:
- `if url1 not in url_to_code or url2 not in url_to_code: continue`

Therefore, mixing datasets safely requires:
1) Mixed pair files (BCB + Camel)
2) A combined mapping file that contains code for **both** sources

---

## 2) Overall Pipeline

We run the mix pipeline in **two steps**:

### Step 1 — Sample 10% from BCB (balanced, deterministic)
Generate a reproducible 10% subset of BCB pairs first (to control training size and keep experiments stable).

### Step 2 — Mix BCB(10%) with Camel
Create:
- `train_mix.txt = train_10percent + camel_train`
- `valid_mix.txt = valid_10percent + camel_valid`
- `mix/data.jsonl = concat(bcb_jsonl + camel_jsonl)` with ID prefixes

---

## 3) Step 1 — Create BCB 10% Dataset (Balanced, Deterministic)

### Script
- `1_sample_data.py`

### Command
```bash
python 1_sample_data.py --seed 3 --mode balanced

Output Files
	•	../dataset/train_10percent.txt
	•	../dataset/valid_10percent.txt

Observed Output (from run log)

[IN ] train.txt: total=901028 label0=450166 label1=450862
[OUT] train_10percent.txt: total=90102 label0=45051 label1=45051

[IN ] valid.txt: total=415416 label0=361577 label1=53839
[OUT] valid_10percent.txt: total=41540 label0=20770 label1=20770

✅ Verification results
	•	BCB train 10% size = 90102
	•	BCB valid 10% size = 41540
	•	Both are label-balanced (0/1 = 50:50)
	•	Sampling is deterministic (seed=3)

⸻

4) Step 2 — Mix BCB(10%) + Camel into One Dataset

Script
	•	2_mix_data.py

Command

python 2_mix_data.py \
  --train_data_file_bcb ../dataset/train_10percent.txt \
  --valid_data_file_bcb ../dataset/valid_10percent.txt \
  --train_data_file_more ../../../detect_clones/NiCad/post_process/data/java/camel/train.txt \
  --valid_data_file_more ../../../detect_clones/NiCad/post_process/data/java/camel/valid.txt \
  --bcb_jsonl ../dataset/data.jsonl \
  --more_jsonl ../../../detect_clones/NiCad/post_process/data/java/camel/data.jsonl \
  --seed 3

Mixing Details (What the script does)

4.1 Prefix IDs to avoid collisions
Even though we later confirmed collisions were zero, we still prefix for safety and clarity:
	•	BCB IDs get bcb_ prefix
	•	Camel IDs get camel_ prefix

This makes the mixed dataset self-describing and robust to future extensions.

4.2 Create prefixed pair files
Output:
	•	../dataset/mix/train_bcb.pref.txt
	•	../dataset/mix/valid_bcb.pref.txt
	•	../dataset/mix/train_more.pref.txt
	•	../dataset/mix/valid_more.pref.txt

4.3 Combine code mappings into one data.jsonl
Output:
	•	../dataset/mix/data.jsonl

BCB and Camel data.jsonl are concatenated after prefixing the idx.

4.4 Merge & shuffle into final mixed datasets
Output:
	•	../dataset/train_mix.txt
	•	../dataset/valid_mix.txt

Shuffling is deterministic using seed=3.

⸻

5) Observed Output of run-mix-data.sh

Running:

./run-mix-data.sh

Observed output:

[OK] prefixed pairs: ../dataset/train_10percent.txt -> ../dataset/mix/train_bcb.pref.txt (lines=90102)
[OK] prefixed pairs: ../dataset/valid_10percent.txt -> ../dataset/mix/valid_bcb.pref.txt (lines=41540)
[OK] prefixed pairs: .../camel/train.txt -> ../dataset/mix/train_more.pref.txt (lines=4068)
[OK] prefixed pairs: .../camel/valid.txt -> ../dataset/mix/valid_more.pref.txt (lines=2034)

[OK] appended jsonl: ../dataset/data.jsonl (+9126) with prefix=bcb_
[OK] appended jsonl: .../camel/data.jsonl (+2739) with prefix=camel_

[OK] merged+shuffled: ../dataset/train_mix.txt (total_lines=94170)
[OK] merged+shuffled: ../dataset/valid_mix.txt (total_lines=43574)

✅ Verification results
	•	train_mix.txt = 90102 + 4068 = 94170
	•	valid_mix.txt = 41540 + 2034 = 43574
	•	combined mix/data.jsonl size = 9126 + 2739 = 11865

⸻

6) File-Level Verification and Results

6.1 File existence and line counts

Command:

ls -lh ../dataset/train_mix.txt ../dataset/valid_mix.txt ../dataset/mix/data.jsonl
wc -l ../dataset/train_mix.txt ../dataset/valid_mix.txt ../dataset/mix/data.jsonl

Observed:

94170  ../dataset/train_mix.txt
43574  ../dataset/valid_mix.txt
11865  ../dataset/mix/data.jsonl

✅ Passed.

⸻

6.2 Prefix validation in pair files

Command:

head -n 5 ../dataset/train_mix.txt
grep -m 3 "^bcb_" ../dataset/train_mix.txt
grep -m 3 "^camel_" ../dataset/train_mix.txt

Observed (examples):

bcb_23192841  bcb_5562616  1
...
camel_1310_1184 camel_1125_959 0
...

✅ Both bcb_ and camel_ exist in the final mixed training set.

⸻

6.3 Prefix validation in mix/data.jsonl

Command:

head -n 3 ../dataset/mix/data.jsonl
grep -m 1 '"idx": "bcb_' ../dataset/mix/data.jsonl
grep -m 1 '"idx": "camel_' ../dataset/mix/data.jsonl

Observed (examples):
	•	{"idx": "bcb_10000832", ...}
	•	{"idx": "camel_9_0", ...}

✅ Both namespaces exist in the combined mapping file.

⸻

6.4 Critical loader-level lookup test (no missing ids)

This validates that pair IDs appearing in train_mix.txt are present in mix/data.jsonl (i.e., url_to_code lookup succeeds).

Command:

python - <<'PY'
import json, random
from pathlib import Path

pairs = Path("../dataset/train_mix.txt").read_text().splitlines()
random.seed(3)
sample = random.sample(pairs, 20)

jsonl = Path("../dataset/mix/data.jsonl")
keys = set()
for line in jsonl.open():
    js = json.loads(line)
    keys.add(js["idx"])

miss = 0
for ln in sample:
    a,b,y = ln.split("\t")
    if a not in keys or b not in keys:
        miss += 1
        print("MISSING:", a, b, y)
print("checked:", len(sample), "missing:", miss)
PY

Observed:

checked: 20 missing: 0

✅ This is the most important check: it implies the mixed dataset will not be heavily filtered out by run.py.

⸻

7) Training: Fine-tuning CodeGPT on Mixed Dataset (Next Step)

Key requirement: run.py must load ../dataset/mix/data.jsonl.

In this codebase, the mapping file is loaded from:

<dataset_dir> / {test_type} / data.jsonl

Therefore, when using the mixed dataset:
	•	--test_type mix
	•	pair files: train_mix.txt, valid_mix.txt

Expected arguments
	•	--train_data_file=../dataset/train_mix.txt
	•	--eval_data_file=../dataset/valid_mix.txt
	•	--test_type mix

(Example) CodeGPT training command

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

Training-time sanity checks (log)

When training starts, confirm:
	•	dataset logging shows near pairs_loaded ≈ 94170
	•	Num examples matches expected scale

⸻

8) Next: Repeat the Same Mixed Dataset for CodeBERT

After CodeGPT is completed, the same mixed dataset artifacts will be reused:
	•	../dataset/train_mix.txt
	•	../dataset/valid_mix.txt
	•	../dataset/mix/data.jsonl

Then CodeBERT fine-tuning runs with:
	•	--test_type mix
	•	pair files pointing to the mixed files

⸻

Appendix A — Commands Used (Copy/Paste)

A.1 Mix pipeline

# 1) Sample BCB 10% (balanced)
python 1_sample_data.py --seed 3 --mode balanced

# 2) Mix BCB(10%) + Camel (prefix + combined jsonl)
python 2_mix_data.py \
  --train_data_file_bcb ../dataset/train_10percent.txt \
  --valid_data_file_bcb ../dataset/valid_10percent.txt \
  --train_data_file_more ../../../detect_clones/NiCad/post_process/data/java/camel/train.txt \
  --valid_data_file_more ../../../detect_clones/NiCad/post_process/data/java/camel/valid.txt \
  --bcb_jsonl ../dataset/data.jsonl \
  --more_jsonl ../../../detect_clones/NiCad/post_process/data/java/camel/data.jsonl \
  --seed 3

A.2 Verification

# Counts
wc -l ../dataset/train_mix.txt ../dataset/valid_mix.txt ../dataset/mix/data.jsonl

# Prefix check
grep -m 3 "^bcb_" ../dataset/train_mix.txt
grep -m 3 "^camel_" ../dataset/train_mix.txt

# Loader-level lookup sample test
python - <<'PY'
import json, random
from pathlib import Path

pairs = Path("../dataset/train_mix.txt").read_text().splitlines()
random.seed(3)
sample = random.sample(pairs, 20)

jsonl = Path("../dataset/mix/data.jsonl")
keys = set()
for line in jsonl.open():
    js = json.loads(line)
    keys.add(js["idx"])

miss = 0
for ln in sample:
    a,b,y = ln.split("\t")
    if a not in keys or b not in keys:
        miss += 1
        print("MISSING:", a, b, y)
print("checked:", len(sample), "missing:", miss)
PY

