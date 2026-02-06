# 1) Create a deterministic 10% subset of BigCloneBench (BCB)
#    - Uses a fixed random seed for reproducibility (seed=3)
#    - --mode balanced makes the sampled set label-balanced (0/1 = 50:50)
#    - Outputs (expected):
#        ../dataset/train_10percent.txt
#        ../dataset/valid_10percent.txt
python 1_sample_data.py --seed 3 --mode balanced


# 2) Build a mixed dataset: BCB(10%) + Camel
#    - Merges pair files (id1, id2, label) from:
#        * BCB:  ../dataset/train_10percent.txt, ../dataset/valid_10percent.txt
#        * Camel: ../../../detect_clones/.../camel/train.txt, valid.txt
#    - Creates a combined code mapping (data.jsonl) by concatenating:
#        * BCB mapping:  ../dataset/data.jsonl
#        * Camel mapping: ../../../detect_clones/.../camel/data.jsonl
#    - Prefixes IDs (e.g., bcb_*, camel_*) to avoid any potential collisions
#    - Shuffles deterministically using the same seed (seed=3)
#    - Outputs (expected):
#        ../dataset/train_mix.txt
#        ../dataset/valid_mix.txt
#        ../dataset/mix/data.jsonl
python 2_mix_data.py \
  --train_data_file_bcb ../dataset/train_10percent.txt \
  --valid_data_file_bcb ../dataset/valid_10percent.txt \
  --train_data_file_more ../../../detect_clones/NiCad/post_process/data/java/camel/train.txt \
  --valid_data_file_more ../../../detect_clones/NiCad/post_process/data/java/camel/valid.txt \
  --bcb_jsonl ../dataset/data.jsonl \
  --more_jsonl ../../../detect_clones/NiCad/post_process/data/java/camel/data.jsonl \
  --seed 3