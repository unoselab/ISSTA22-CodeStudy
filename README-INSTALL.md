# Installation Guide: Clone Detection Research Environment

This repository contains the environment setup and benchmarking tools for evaluating Pre-trained Models (PTMs) on the **BigCloneBench** dataset. This setup is optimized for high-performance deep learning on dual NVIDIA RTX 6000 Ada GPUs.

## 1. System Requirements

* **OS:** Ubuntu 22.04+ (or compatible Linux distribution)
* **Hardware:** 2x NVIDIA RTX 6000 Ada (96GB total VRAM)
* **Driver:** NVIDIA Driver version 550.142+
* **CUDA:** 12.4
* **Language:** Python 3.11

## 2. Environment Setup

We recommend using **Miniconda** to manage the research environment. This ensures that CUDA-specific libraries are correctly linked without interfering with system-level packages.

### Step 1: Create the Conda Environment

```bash
conda create -n bigclone python=3.11 -y
conda activate bigclone

```

### Step 2: Install PyTorch with CUDA 12.4 Support

Install the core deep learning framework directly via the `pytorch` and `nvidia` channels to ensure the internal `nvcc` tools match your hardware.

```bash
conda install pytorch torchvision torchaudio pytorch-cuda=12.4 -c pytorch -c nvidia

```

### Step 3: Install Research Dependencies

Use the provided `requirements.txt` to install the Transformers library, database connectors for BigCloneBench, and structural parsing tools.

```bash
pip install -r requirements.txt

```

## 3. Verifying the Setup

Run the following Python snippet to verify that both RTX 6000 GPUs are visible and that the environment can perform parallel operations:

```python
import torch

print(f"CUDA Available: {torch.cuda.is_available()}")
print(f"GPU Count: {torch.cuda.device_count()}")

for i in range(torch.cuda.device_count()):
    print(f"GPU {i}: {torch.cuda.get_device_name(i)}")
    # Test tensor allocation on each GPU
    x = torch.rand(1000, 1000).to(f'cuda:{i}')
    print(f"Successfully allocated tensor on GPU {i}")

```

---

## 4. Scientific and Outreach Context

This setup is a core part of our ongoing research into **AI-Driven Software Intelligence and Collaboration**. A primary goal of this repository is the **mentorship of undergraduate and graduate researchers** through the full lifecycle of high-impact projects.

* **Research Focus:** We leverage Large Language Models (LLMs) and datasets like BigCloneBench to automate complex software engineering tasks such as code summarization and clone detection.
* **Mentorship:** Students contribute to this project by managing the AI infrastructure, configuring CUDA-accelerated environments, and conducting large-scale benchmarking.
* **Preparation:** By guiding students from initial environment design to the deployment of models like **SYNCode**, we are preparing the next generation of engineers for a future where AI and human expertise work in tandem.

This infrastructure supports research that has been recognized at premier venues, including the **Best Paper Award at IEEE SERA 2025** and extensive studies presented at **ISSTA**.

---
