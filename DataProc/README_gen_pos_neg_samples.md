# Generating Positive & Negative Samples for Clone Detection

This guide explains how we prepare training data for our code clone detection models. Specifically, it details how we calculate and generate **Positive Samples** (clones) and **Negative Samples** (non-clones) from our dataset.

## 1. Math Background: Counting Pairs

To create a training dataset, we need to form "pairs" of functions. Understanding how many unique pairs exist in a group is crucial for balancing our data.

### The "Handshake" Analogy (Combinatorics)

Imagine a Clone Group containing **4 functions** (A, B, C, D). Since they are all clones of each other, every function must be paired with every _other_ function. This forms a **Complete Graph**.

**How to calculate the number of pairs:**

1. **Connections:** Each of the 4 functions can connect to 3 other people (itself excluded).

2. **Removing Duplicates:** A connection from A to B is the same as B to A. We must divide by 2 to remove this double counting.

The General FormulaFor any group of size $N$, the maximum number of unique pairs is calculated using the "N choose 2" formula:$$\text{Total Pairs} = \binom{N}{2} = \frac{N(N-1)}{2}$$Example:Clone Group Size: 5 functionsCalculation: $\frac{5 \times 4}{2} = 10$ pairs.

---

## 2. Types of Samples

### ✅ Positive Samples (Label 1)

-   **Definition:** Pairs of functions that are **semantic clones** (do the same thing).
-   **Source:** All possible pairs **within** the same Clone Group.
-   **Calculation:** We sum the pairs formula for every clone group in the dataset.

### ❌ Negative Samples (Label 0)

-   **Definition:** Pairs of functions that are **functionally different**.
-   **Source:** Pairs formed by picking functions from **different** Clone Groups.
-   **Calculation:** The total capacity for negative samples is huge (Total Universe of Pairs - Positive Pairs).
-   **Balancing:** Since negative pairs vastly outnumber positive ones, we **randomly sample** a specific number of negative pairs to match the number of positive pairs (1:1 ratio) to prevent training bias.

---

## 3. How to Run the Script

We use the `gen_neg_clone_sample.py` script to automatically calculate these statistics and generate the balanced negative samples.

### Prerequisites

Ensure you have run `gen_init_train_sample.py` first to generate unique `func_id`s for the dataset.

### Command

```bash
python gen_neg_clone_sample.py

```

### Script Output (Console)

The script will print a detailed breakdown of the math for the current dataset:

```text
=== Detailed Calculation of Dataset Capacity ===
1. Total Functions (N): 2,739
   - Total possible pairs (Universe) = 3,749,691 pairs

2. Max Possible Positive Samples (Clones): 3,822
   - Calculation: Sum of pairs within each clone group.

3. Max Possible Negative Samples (Non-Clones): 3,745,869
   - Formula: Universe - Positives

```

### Generated Files

1. **`data/nicad_camel_neg_samples.txt`**: The final training list. Format:

```text
1423_0    99_2      0
1423_0    105_1     0
...

```

2. **`data/display_neg_sample.md`**: A Markdown table for quick inspection on GitHub.
3. **`display_neg_sample.html`**: A full HTML page with side-by-side code comparison.

---

## 4. Visual Inspection

The script generates a Markdown report (`data/display_neg_sample.md`) to help you verify the quality of the negative samples directly in your browser or editor.

### Example Output (from display_neg_sample.md)

| Pair ID | Function A (Source)  | Function B (Target) |
| ------- | -------------------- | ------------------- |
| **#1**  | **ID:** `1423_0`<br> |

<br>`Camel.load()`<br>

<br><pre>public void load() {<br>

<br> super.load();<br>

<br>...</pre> | **ID:** `99_2`<br>

<br>`Kafka.send()`<br>

<br><pre>public void send() {<br>

<br> producer.send(msg);<br>

<br>...</pre> |
| **#2** | **ID:** `502_4`<br>

<br>`Util.parse()`<br>

<br><pre>public int parse(String s) {<br>

<br> return Integer.parseInt(s);<br>

<br>...</pre> | **ID:** `12_8`<br>

<br>`Auth.login()`<br>

<br><pre>public boolean login() {<br>

<br> if (checkCredentials()) ...<br>

<br>...</pre> |

**Note:** The HTML report (`display_neg_sample.html`) provides a more detailed side-by-side view with syntax highlighting support if opened in a browser.
