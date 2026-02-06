#!/usr/bin/env python3
import argparse
import json
import random
from pathlib import Path

DEFAULT_SEED = 3

def prefix_pairs(in_path: Path, out_path: Path, prefix: str):
    """
    Prefix pair identifiers in a clone-pair TSV file to avoid ID collisions.
    Supports both tab- and space-separated files.
    Format: <id1> <id2> <label>
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with in_path.open("r", encoding="utf-8") as fin, out_path.open("w", encoding="utf-8") as fout:
        for line in fin:
            line = line.strip()
            if not line:
                continue
            parts = line.split()  # IMPORTANT: handles both tabs and spaces
            if len(parts) != 3:
                continue
            u1, u2, y = parts
            fout.write(f"{prefix}{u1}\t{prefix}{u2}\t{y}\n")  # output TSV normalized
            n += 1
    print(f"[OK] prefixed pairs: {in_path} -> {out_path} (lines={n})")


def build_mix_jsonl(bcb_jsonl: Path, more_jsonl: Path, out_jsonl: Path):
    out_jsonl.parent.mkdir(parents=True, exist_ok=True)
    if out_jsonl.exists():
        out_jsonl.unlink()

    def append_with_prefix(src: Path, prefix: str):
        n = 0
        with src.open("r", encoding="utf-8") as fin, out_jsonl.open("a", encoding="utf-8") as fout:
            for line in fin:
                line = line.strip()
                if not line:
                    continue
                js = json.loads(line)
                js["idx"] = f"{prefix}{js['idx']}"
                fout.write(json.dumps(js, ensure_ascii=False) + "\n")
                n += 1
        print(f"[OK] appended jsonl: {src} (+{n}) with prefix={prefix}")

    append_with_prefix(bcb_jsonl, "bcb_")
    append_with_prefix(more_jsonl, "camel_")  # "more" == Camel in this setup

def merge_shuffle(out_path: Path, files, seed: int):
    rnd = random.Random(seed)
    lines = []
    for f in files:
        with Path(f).open("r", encoding="utf-8") as fin:
            lines.extend([ln for ln in fin if ln.strip()])
    rnd.shuffle(lines)
    out_path.write_text("".join(lines), encoding="utf-8")
    print(f"[OK] merged+shuffled: {out_path} (total_lines={len(lines)})")

def main():
    p = argparse.ArgumentParser(description="Create mixed (BCB + more) train/valid + combined data.jsonl.")
    p.add_argument("--seed", type=int, default=DEFAULT_SEED)

    # Required pair files
    p.add_argument("--train_data_file_bcb", type=str, required=True)
    p.add_argument("--train_data_file_more", type=str, required=True)
    p.add_argument("--valid_data_file_bcb", type=str, required=True)
    p.add_argument("--valid_data_file_more", type=str, required=True)

    # Required jsonl mapping files
    p.add_argument("--bcb_jsonl", type=str, required=True, help="BCB data.jsonl path")
    p.add_argument("--more_jsonl", type=str, required=True, help="Camel (or other) data.jsonl path")

    # Outputs
    p.add_argument("--out_dir", type=str, default="../dataset/mix", help="Directory for prefixed files + mix data.jsonl")
    p.add_argument("--out_train_mix", type=str, default="../dataset/train_mix.txt")
    p.add_argument("--out_valid_mix", type=str, default="../dataset/valid_mix.txt")

    args = p.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1) Prefix pair files
    bcb_train_p  = out_dir / "train_bcb.pref.txt"
    bcb_valid_p  = out_dir / "valid_bcb.pref.txt"
    more_train_p = out_dir / "train_more.pref.txt"
    more_valid_p = out_dir / "valid_more.pref.txt"

    prefix_pairs(Path(args.train_data_file_bcb),  bcb_train_p,  "bcb_")
    prefix_pairs(Path(args.valid_data_file_bcb),  bcb_valid_p,  "bcb_")
    prefix_pairs(Path(args.train_data_file_more), more_train_p, "camel_")
    prefix_pairs(Path(args.valid_data_file_more), more_valid_p, "camel_")

    # 2) Create combined jsonl
    mix_jsonl = out_dir / "data.jsonl"
    build_mix_jsonl(Path(args.bcb_jsonl), Path(args.more_jsonl), mix_jsonl)

    # 3) Create train_mix / valid_mix (shuffled)
    train_mix = Path(args.out_train_mix)
    valid_mix = Path(args.out_valid_mix)

    merge_shuffle(train_mix, [bcb_train_p, more_train_p], seed=args.seed)
    merge_shuffle(valid_mix, [bcb_valid_p, more_valid_p], seed=args.seed)

    print("\nDone.")
    print(f"- train_mix: {train_mix}")
    print(f"- valid_mix: {valid_mix}")
    print(f"- mix jsonl:  {mix_jsonl}")

if __name__ == "__main__":
    main()