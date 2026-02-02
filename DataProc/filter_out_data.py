#!/usr/bin/env python3
import argparse
import json
import os
import re
import sys
from typing import Dict, Any, List

"""
Option A (recommended): drop whole group if it contains any test snippet

python filter_out_tests.py \
  --input data/step2_nicad_camel-java_sim0.7_classes_fqn.jsonl \
  --output data/nicad_camel_clone_func.jsonl \
  --mode drop_group_if_any_test

---  

Option B: only remove the test snippets, keep group if ≥2 remain

python filter_out_tests.py \
  --input step2_nicad_camel-java_sim0.7_classes_fqn.jsonl \
  --output nicad_camel_clone_func.jsonl \
  --mode drop_only_test_sources \
  --min_remaining 2
"""

# ---- Test detection rules ----
# 1) directory path in sources[].file
TEST_DIR_PATTERNS = [
    r"(^|/)src/test(/|/java/|/resources/|$)",
    r"(^|/)src/it(/|$)",          # integration tests (some repos)
    r"(^|/)src/integration-test(/|$)",
    r"(^|/)test(/|$)",
    r"(^|/)tests(/|$)",
]

# 2) java file name in sources[].file
# common conventions: *Test.java, *Tests.java, *TestCase.java, *IT.java, *ITCase.java
TEST_FILENAME_PATTERNS = [
    r"Test\.java$",
    r"Tests\.java$",
    r"TestCase\.java$",
    r"IT\.java$",
    r"ITCase\.java$",
    r"IntegrationTest\.java$",
]

TEST_DIR_RES = [re.compile(p) for p in TEST_DIR_PATTERNS]
TEST_FILE_RES = [re.compile(p) for p in TEST_FILENAME_PATTERNS]


def is_test_path(path: str) -> bool:
    """Return True if the path looks like a test file by dir or filename."""
    norm = path.replace("\\", "/")  # just in case
    for r in TEST_DIR_RES:
        if r.search(norm):
            return True
    base = os.path.basename(norm)
    for r in TEST_FILE_RES:
        if r.search(base):
            return True
    return False


def group_has_any_test_source(obj: Dict[str, Any]) -> bool:
    for s in obj.get("sources", []):
        if is_test_path(s.get("file", "")):
            return True
    return False


def filter_sources_remove_tests(obj: Dict[str, Any]) -> Dict[str, Any]:
    """Remove test sources from a group, update nclones accordingly."""
    sources = obj.get("sources", [])
    kept = [s for s in sources if not is_test_path(s.get("file", ""))]
    new_obj = dict(obj)
    new_obj["sources"] = kept
    new_obj["nclones"] = len(kept)
    return new_obj


def main():
    ap = argparse.ArgumentParser(
        description="Filter out test functions from a NiCad clone JSONL file using path + filename heuristics."
    )
    ap.add_argument("--input", required=True, help="Input JSONL file")
    ap.add_argument("--output", required=True, help="Output JSONL file")
    ap.add_argument(
        "--mode",
        choices=["drop_group_if_any_test", "drop_only_test_sources"],
        default="drop_group_if_any_test",
        help=(
            "drop_group_if_any_test: remove entire clone group if any source is a test file.\n"
            "drop_only_test_sources: remove only the test sources; keep group if >=2 sources remain."
        ),
    )
    ap.add_argument(
        "--min_remaining",
        type=int,
        default=2,
        help="When using drop_only_test_sources, keep a group only if at least this many sources remain (default 2).",
    )
    args = ap.parse_args()

    in_path = args.input
    out_path = args.output

    kept_groups = 0
    dropped_groups = 0
    dropped_sources = 0
    total_groups = 0

    with open(in_path, "r", encoding="utf-8") as fin, open(out_path, "w", encoding="utf-8") as fout:
        for line_no, line in enumerate(fin, 1):
            line = line.strip()
            if not line:
                continue
            total_groups += 1
            try:
                obj = json.loads(line)
            except Exception as e:
                print(f"[ERROR] JSON parse failed at line {line_no}: {e}", file=sys.stderr)
                continue

            if args.mode == "drop_group_if_any_test":
                if group_has_any_test_source(obj):
                    dropped_groups += 1
                    continue
                fout.write(json.dumps(obj, ensure_ascii=False) + "\n")
                kept_groups += 1

            else:  # drop_only_test_sources
                before = len(obj.get("sources", []))
                new_obj = filter_sources_remove_tests(obj)
                after = len(new_obj.get("sources", []))
                dropped_sources += max(0, before - after)

                # keep only meaningful clone groups
                if after >= args.min_remaining:
                    fout.write(json.dumps(new_obj, ensure_ascii=False) + "\n")
                    kept_groups += 1
                else:
                    dropped_groups += 1

    print("Done.")
    print(f"  Input groups:   {total_groups}")
    print(f"  Kept groups:    {kept_groups}")
    print(f"  Dropped groups: {dropped_groups}")
    if args.mode == "drop_only_test_sources":
        print(f"  Dropped sources:{dropped_sources}")
    print(f"  Output written: {out_path}")


if __name__ == "__main__":
    main()