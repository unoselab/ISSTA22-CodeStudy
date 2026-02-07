#!/usr/bin/env python3
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# ===============================
# Fine-tuning comparison results
# ===============================

models = ["CodeGPT-BCB10", "CodeGPT-BCB10 + Camel"]

precision = [0.6769, 0.7781]
recall    = [0.5324, 0.7591]
f1        = [0.4125, 0.7584]

metrics = ["Precision", "Recall", "F1"]
values = [precision, recall, f1]

# Plot setup
x = np.arange(len(metrics))
width = 0.35

plt.figure(figsize=(7, 4))

plt.bar(x - width/2, [v[0] for v in values], width, label=models[0])
plt.bar(x + width/2, [v[1] for v in values], width, label=models[1])

plt.xticks(x, metrics)
plt.ylim(0, 1.0)
plt.ylabel("Score")
plt.title("Cross-Domain Performance on Camel Test Set")
plt.legend()
plt.tight_layout()

# Output path
out_dir = Path(".")
out_path = out_dir / "fine-tune-camel.png"

plt.savefig(out_path, dpi=200)
plt.close()

print(f"[OK] Saved figure to {out_path.resolve()}")
