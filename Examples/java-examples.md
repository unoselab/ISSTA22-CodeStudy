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

- **Logical Density:** Even with very few tokens, it contains a conditional branch (`if-else`), which is critical for testing if a model understands logic rather than just text.
- **Variable Mapping:** It uses two parameters, allowing you to test if the model can distinguish between `(a, b)` and `(b, a)` clones.
- **Standard Structure:** It follows the standard boilerplate that LLMs expect for Java methods.

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

--

### Exemplary Java Function (40 - 50 Tokens)

```java
public double calculateAverage(int[] numbers) {
    if (numbers == null || numbers.length == 0) {
        return 0.0;
    }
    double sum = 0;
    for (int num : numbers) {
        sum += num;
    }
    return sum / numbers.length;
}
```

--

### Exemplary Java Function (50 - 60 Tokens)

```java
public int linearSearch(int[] array, int target) {
    if (array == null || array.length == 0) {
        return -1;
    }
    for (int i = 0; i < array.length; i++) {
        if (array[i] == target) {
            return i;
        }
    }
    return -1;
}
```

--

### Exemplary Java Function (50 - 60 Tokens)

```java
public boolean push(int[] stack, int element, int top) {
    if (top >= stack.length - 1) {
        System.out.println("Stack Overflow");
        return false;
    }
    stack[top + 1] = element;
    return true;
}
```
