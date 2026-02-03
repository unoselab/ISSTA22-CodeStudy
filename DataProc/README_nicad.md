# README_nicad.md
NiCad Clone Data with Fully Qualified Names  
`step2_nicad_camel-java_sim0.7_classes_fqn.jsonl`

---

## 1. Artifact Description

This README documents the generation process and structure of the file:

```
step2_nicad_camel-java_sim0.7_classes_fqn.jsonl
```

This file contains **NiCad clone classes** detected from the `camel-java` project at
**similarity threshold 0.7**, enriched with **fully qualified identifiers** for
each clone source.

The goal of this step is to make clone instances easier to interpret, analyze,
and reference by attaching a readable identifier of the form:

```
package.ClassName.methodSignature
```

---

## 2. Generation Pipeline

The dataset is produced using the following pipeline:

```
camel-java source code
        ↓
NiCad clone detection (classes, sim = 0.7)
        ↓
NiCad XML clone report
        ↓
Step 1: XML → JSONL conversion
        ↓
Step 2: Add fully qualified names
        ↓
step2_nicad_camel-java_sim0.7_classes_fqn.jsonl
```

---

## 3. Step 1: NiCad Clone Detection

NiCad is executed on the `camel-java` project with:

- Language: Java  
- Granularity: class-level clones  
- Similarity threshold: 0.7  

NiCad groups similar code fragments into **clone classes**.  
Each clone class contains multiple **clone sources** extracted from the project.

The NiCad XML output is converted into JSON Lines (JSONL) format, where:

- Each line represents one clone class
- Each clone class contains a `sources` list
- Each `sources[i]` entry includes:
  - `file`: Java source file path
  - `range`: line range
  - `nlines`: number of lines
  - `code`: extracted code fragment

Output of Step 1:

```
step1_nicad_camel-java_sim0.7_classes.jsonl
```

---

## 4. Step 2: Adding Fully Qualified Names

Step 2 post-processes the Step 1 JSONL file and produces:

```
step2_nicad_camel-java_sim0.7_classes_fqn.jsonl
```

For each clone source, the script adds:

```
sources[].qualified_name
```

---

## 5. Qualified Name Construction

The qualified name is constructed as:

```
<package>.<ClassName>.<methodName>(<parameters>)
```

### Component extraction

- **Package**  
  Extracted from the Java source file using the `package ...;` declaration.

- **Class name**  
  Derived from the Java file name (`FileName.java → FileName`).

- **Method signature**  
  Extracted from the code fragment header using lightweight regex-based parsing.
  The last identifier before `(` (excluding Java control keywords) is used as
  the method name. Parameter text is normalized and preserved when available.

### Fallback behavior

- If the package cannot be determined, the package prefix is omitted.
- If the method name cannot be determined, `<unknown>()` is used.

### Example

```json
{
  "qualified_name": "org.apache.camel.component.caffeine.cache.CaffeineCacheProducerTest.testCacheInvalidateAllWithoutKeys()"
}
```

---

## 6. Script Execution

Typical usage:

```bash
python step2_add_qualified_name.py \
  --in  step1_nicad_camel-java_sim0.7_classes.jsonl \
  --out step2_nicad_camel-java_sim0.7_classes_fqn.jsonl \
  --projects-root /path/to/project/root
```

The `--projects-root` option is required to resolve relative paths such as
`systems/camel-java/...`.

---

## 7. Output Characteristics

- Output format remains **JSONL**
- Original clone data is preserved
- One additional field is added per clone source:
  - `sources[].qualified_name`
- Processing is streaming and memory-efficient
- Java source files are cached to reduce disk I/O

---

## 8. Statistics Reported

After processing, the script prints summary statistics to **stderr**:

- Number of clone classes processed
- Total number of clone instances
- Average clones per class (all classes)
- Average clones per class (classes with clones)

Example:

```
[stats] classes parsed = 1216
[stats] nclones total  = 4559
[stats] nclones avg (all classes)          = 3.749
[stats] nclones avg (classes with nclones) = 3.900
```

---

## 9. Limitations

- Method signature extraction is heuristic and regex-based (no Java AST)
- Complex Java constructs (e.g., lambdas, anonymous classes) may result in
  `<unknown>()`
- Class names are assumed to match file names (standard Java convention)

---

## 10. Summary

`step2_nicad_camel-java_sim0.7_classes_fqn.jsonl` is a NiCad clone-class dataset
augmented with fully qualified, human-readable identifiers, enabling efficient
analysis and reporting of Java clone instances.
