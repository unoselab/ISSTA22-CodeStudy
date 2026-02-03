import json
import random
import sys
import os
import html

# 기본 설정 (Default Configuration)
DEFAULT_INPUT = "data/nicad_camel_clone_func_small.jsonl"
OUTPUT_JSONL = "data/negative_samples.jsonl"
OUTPUT_HTML = "display_neg_sample.html"

def generate_html_report(pairs, output_file=OUTPUT_HTML):
    """
    Generates an HTML report to visualize the generated negative pairs side-by-side.
    """
    html_content = [
        "<html><head><style>",
        "body { font-family: sans-serif; margin: 20px; background-color: #f9f9f9; }",
        "h2 { color: #333; }",
        ".pair-container { background: white; border: 1px solid #ddd; margin-bottom: 30px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }",
        ".pair-header { font-weight: bold; margin-bottom: 10px; padding-bottom: 5px; border-bottom: 2px solid #eee; color: #555; }",
        ".code-row { display: flex; gap: 20px; }",
        ".code-col { flex: 1; min-width: 0; }", # min-width: 0 forces flex items to shrink
        ".meta-info { font-size: 0.85em; color: #666; margin-bottom: 5px; background: #f0f0f0; padding: 5px; border-radius: 4px; }",
        "pre { background-color: #f4f4f4; padding: 10px; border: 1px solid #ccc; overflow-x: auto; font-size: 0.8em; font-family: Consolas, monospace; height: 300px; }",
        ".label-badge { background-color: #e74c3c; color: white; padding: 2px 6px; border-radius: 3px; font-size: 0.8em; vertical-align: middle; }",
        "</style></head><body>",
        f"<h2>Generated Negative Samples (Label 0) - Total {len(pairs)} Pairs</h2>",
        "<p>These pairs represent functions from <b>different</b> clone groups (different logic).</p>"
    ]

    for i, pair in enumerate(pairs, 1):
        f1 = pair['func1']
        f2 = pair['func2']
        meta = pair['meta']

        # Meta info strings
        info1 = f"<b>ClassID:</b> {meta['classid1']}<br><b>File:</b> {f1.get('file', 'N/A')}<br><b>Name:</b> {html.escape(f1.get('qualified_name', 'Unknown'))}"
        info2 = f"<b>ClassID:</b> {meta['classid2']}<br><b>File:</b> {f2.get('file', 'N/A')}<br><b>Name:</b> {html.escape(f2.get('qualified_name', 'Unknown'))}"

        # Code content
        code1 = html.escape(f1.get('code', ''))
        code2 = html.escape(f2.get('code', ''))

        html_content.append(f"""
        <div class="pair-container">
            <div class="pair-header">
                Pair #{i} <span class="label-badge">Negative (Non-Clone)</span>
            </div>
            <div class="code-row">
                <div class="code-col">
                    <div class="meta-info">{info1}</div>
                    <pre>{code1}</pre>
                </div>
                <div class="code-col">
                    <div class="meta-info">{info2}</div>
                    <pre>{code2}</pre>
                </div>
            </div>
        </div>
        """)

    html_content.append("</body></html>")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(html_content))
    print(f"HTML report generated: {output_file}")

def generate_negative_samples(input_file, output_jsonl):
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        return

    print(f"--- Loading data from: {input_file} ---")
    
    # 1. Load Data
    groups = {}     # {classid: [func1, func2, ...]}
    flat_funcs = [] # list of (classid, func_data)
    
    total_positive_pairs = 0

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line: continue
                try:
                    data = json.loads(line)
                    class_id = data.get("classid")
                    sources = data.get("sources", [])
                    
                    if class_id is None or not sources:
                        continue
                        
                    groups[class_id] = sources
                    
                    # Calculate potential positive pairs (nC2) for reference
                    n = len(sources)
                    if n > 1:
                        total_positive_pairs += (n * (n - 1)) // 2
                    
                    for src in sources:
                        flat_funcs.append((class_id, src))
                        
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    print(f"Loaded {len(groups)} groups.")
    
    if len(groups) < 2:
        print("Error: Need at least 2 clone groups to generate negative samples.")
        return

    # 2. Generate Negative Pairs
    # Target: Match the number of positive pairs (or at least 10 for small data)
    target_neg_count = total_positive_pairs if total_positive_pairs > 0 else 10
    print(f"--- Generating {target_neg_count} Negative Samples ---")
    
    generated_pairs_list = []
    seen_pairs = set()
    attempts = 0
    max_attempts = target_neg_count * 20 
    
    while len(generated_pairs_list) < target_neg_count and attempts < max_attempts:
        attempts += 1
        
        # Pick two random functions
        f1 = random.choice(flat_funcs)
        f2 = random.choice(flat_funcs)
        
        id1, data1 = f1
        id2, data2 = f2
        
        # Must be from different groups
        if id1 != id2:
            # Create a unique key to avoid duplicates
            # Use qualified_name + range or code snippet hash as key
            k1 = data1.get("qualified_name", "") + str(data1.get("range", ""))
            k2 = data2.get("qualified_name", "") + str(data2.get("range", ""))
            
            # Sort keys to treat (A, B) same as (B, A)
            pair_key = tuple(sorted((k1, k2)))
            
            if pair_key not in seen_pairs:
                seen_pairs.add(pair_key)
                
                pair_entry = {
                    "label": 0,
                    "func1": data1,
                    "func2": data2,
                    "meta": {
                        "classid1": id1,
                        "classid2": id2
                    }
                }
                generated_pairs_list.append(pair_entry)

    print(f"Done. Generated {len(generated_pairs_list)} unique negative pairs.")

    # 3. Save to JSONL
    try:
        with open(output_jsonl, 'w', encoding='utf-8') as out_f:
            for p in generated_pairs_list:
                out_f.write(json.dumps(p) + "\n")
        print(f"JSONL saved to: {output_jsonl}")
    except Exception as e:
        print(f"Error writing JSONL: {e}")

    # 4. Generate HTML Report
    generate_html_report(generated_pairs_list)

if __name__ == "__main__":
    input_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_INPUT
    
    # Remove old files if exist
    if os.path.exists(OUTPUT_JSONL): os.remove(OUTPUT_JSONL)
    if os.path.exists(OUTPUT_HTML): os.remove(OUTPUT_HTML)
        
    generate_negative_samples(input_path, OUTPUT_JSONL)