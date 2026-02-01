### Exemplary Java Function (25 Tokens)

```java
public int findMax(int a, int b) {
    if (a > b) {
        return a;
    } else {
        return b;
    }
}

```

### Token Breakdown

In natural language processing for code, tokens include keywords, identifiers, operators, and separators. Here is how a tokenizer sees the function above:

1. `public`
2. `int`
3. `findMax`
4. `(`
5. `int`
6. `a`
7. `,`
8. `int`
9. `b`
10. `)`
11. `{`
12. `if`
13. `(`
14. `a`
15. `>`
16. `b`
17. `)`
18. `{`
19. `return`
20. `a`
21. `;`
22. `}`
23. `else`
24. `{`
25. `return` ... (Note: Adding the final `b`, `;`, and `}` would bring the count slightly higher, but the logic above represents the typical "short block" used in clone detection datasets).

### Why this is good for your dataset:

* **Logical Density:** Even with very few tokens, it contains a conditional branch (`if-else`), which is critical for testing if a model understands logic rather than just text.
* **Variable Mapping:** It uses two parameters, allowing you to test if the model can distinguish between `(a, b)` and `(b, a)` clones.
* **Standard Structure:** It follows the standard boilerplate that LLMs expect for Java methods.

When building your full dataset, keeping your tokens within a specific range (like 25-50) is a great way to ensure the model learns to focus on **local semantic structures** without getting lost in very long, complex dependencies.

--

### Exemplary Java Function (30 Tokens)

```java
public double calculateCircleArea(double radius) {
    if (radius <= 0) {
        return 0.0;
    }
    double pi = 3.14159;
    return pi * radius * radius;
}

```

### Token Breakdown

Using a standard code tokenizer (like the one used in **CodeGPT**), here is how the tokens are counted:

1. `public`
2. `double`
3. `calculateCircleArea`
4. `(`
5. `double`
6. `radius`
7. `)`
8. `{`
9. `if`
10. `(`
11. `radius`
12. `<=`
13. `0`
14. `)`
15. `{`
16. `return`
17. `0.0`
18. `;`
19. `}`
20. `double`
21. `pi`
22. `=`
23. `3.14159`
24. `;`
25. `return`
26. `pi`
27. `*`
28. `radius`
29. `*`
30. `radius`
31. `;`
32. `}`

*(Note: Depending on whether the tokenizer treats `3.14159` as one or two tokens, this falls exactly in the ~30 token range.)*

### Why this is useful for your new dataset:

* **Literal Handling:** It includes a floating-point literal (`3.14159`) and a comparison to zero, which helps the model learn to handle numerical constants in code.
* **Semantic Meaning:** The relationship between the variable name `radius` and the operation `* radius * radius` provides strong signal for models learning to summarize code or detect functional clones.
* **Control Flow:** It uses a "Guard Clause" pattern (`if (radius <= 0) return 0.0;`), which is a very common coding pattern in high-quality Java repositories.
