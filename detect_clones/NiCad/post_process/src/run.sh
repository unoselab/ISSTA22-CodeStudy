LOG=../data/java/pipeline.log

mkdir -p ../data/java && \
echo "============================================================" | tee -a "$LOG" && \
echo "[STEP 1] 1_nicad_xml_to_jsonl.py  $(date)" | tee -a "$LOG" && \
echo "============================================================" | tee -a "$LOG" && \
python 1_nicad_xml_to_jsonl.py \
  --xml ../input/camel-java_functions-blind-clones-0.30-classes-withsource.xml \
  --out ../data/java/step1_nicad_camel_sim0.7_classes.jsonl \
  --mode class \
  2>&1 | tee -a "$LOG"

echo "------------------------------------------------------------" | tee -a "$LOG" && \
echo "[STEP 2] 2_java_qmethod_ts.py  $(date)" | tee -a "$LOG" && \
echo "------------------------------------------------------------" | tee -a "$LOG" && \
python 2_java_qmethod_ts.py \
  --in ../data/java/step1_nicad_camel_sim0.7_classes.jsonl \
  --out ../data/java/camel_sim0.7.jsonl \
  --projects-root ../.. \
  2>&1 | tee -a "$LOG"

echo "------------------------------------------------------------" | tee -a "$LOG" && \
echo "[STEP 3] 3_filter_out_data.py  $(date)" | tee -a "$LOG" && \
echo "------------------------------------------------------------" | tee -a "$LOG" && \
python 3_filter_out_data.py \
  --input ../data/java/camel_sim0.7.jsonl \
  --output ../data/java/nicad_camel_clone_func.jsonl \
  --mode drop_group_if_any_test \
  --max_clones 20 \
  2>&1 | tee -a "$LOG"

echo "------------------------------------------------------------" | tee -a "$LOG" && \
echo "[STEP 4] 4_gen_init_train_sample.py  $(date)" | tee -a "$LOG" && \
echo "------------------------------------------------------------" | tee -a "$LOG" && \
python 4_gen_init_train_sample.py \
  ../data/java/nicad_camel_clone_func.jsonl \
  ../data/java/nicad_camel_clone_data.jsonl \
  2>&1 | tee -a "$LOG"

echo "------------------------------------------------------------" | tee -a "$LOG" && \
echo "[STEP 5] 5_gen_neg_clone_sample.py  $(date)" | tee -a "$LOG" && \
echo "------------------------------------------------------------" | tee -a "$LOG" && \
python 5_gen_neg_clone_sample.py \
  ../data/java/nicad_camel_clone_data.jsonl \
  2>&1 | tee -a "$LOG"
