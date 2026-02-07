# 1) Create a deterministic 10% subset of BigCloneBench (BCB)
#    - Uses a fixed random seed for reproducibility (seed=3)
#    - --mode balanced makes the sampled set label-balanced (0/1 = 50:50)
#    - Outputs (expected):
#        ../dataset/train_10percent.txt
#        ../dataset/valid_10percent.txt
python 1_sample_data.py --seed 3 --mode balanced

# 2) Build a mixed dataset: BCB(10%) + Other Domain (e.g., Camel)
#    - Merges clone-pair files (id1, id2, label) from:
#        * BCB (10% sampled):
#            - ../dataset/train_10percent.txt
#            - ../dataset/valid_10percent.txt
#        * Other domain (specified via --otherdomain_name, e.g., Camel):
#            - ../../../detect_clones/.../<otherdomain>/train.txt
#            - ../../../detect_clones/.../<otherdomain>/valid.txt
#
#    - Optionally prepares an OTHER-DOMAIN-ONLY test set for cross-domain evaluation:
#        * Input:
#            - ../../../detect_clones/.../<otherdomain>/test.txt
#        * Output (new file, no overwrite):
#            - ../dataset/test_<otherdomain>.txt
#
#    - Creates a combined code mapping (mix/data.jsonl) by concatenating:
#        * BCB mapping:
#            - ../dataset/data.jsonl
#        * Other-domain mapping:
#            - ../../../detect_clones/.../<otherdomain>/data.jsonl
#
#    - Prefixes all function IDs to avoid collisions and ensure resolvability:
#        * BCB IDs          -> bcb_<id>
#        * Other-domain IDs -> <otherdomain>_<id>
#
#    - Shuffles merged train / valid sets deterministically
#      using a fixed random seed (seed=3)
#
#    - Outputs (expected):
#        * ../dataset/train_mix.txt
#        * ../dataset/valid_mix.txt
#        * ../dataset/test_<otherdomain>.txt   (optional, other-domain only)
#        * ../dataset/mix/data.jsonl
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


