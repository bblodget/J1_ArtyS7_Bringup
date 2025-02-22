# Fast Loop in Forth: The TIMES ... NEXT Construct

This document describes a non‑standard fast loop construct for Forth that uses a single count parameter to minimize loop overhead. Unlike the standard dual‑parameter `DO ... LOOP` (which supplies both an initial index and a limit), this construct uses the syntax:

  n **TIMES** _block_ **NEXT**

Each iteration decrements the count from \( n \) down to 0. A helper word (`TI`) is provided to access the current loop counter (distinct from the traditional `I` of DO loops).

---

## Motivation

Standard Forth loops (i.e. `DO ... LOOP`) push two control values (the index and the limit) onto the return stack. Although flexible, they are more heavyweight than necessary if all you need is a simple countdown. The fast loop approach:

- **Reduces Overhead:** Only one parameter (the count \( n \)) is used.
- **Simplifies the Loop:** Each iteration simply decrements the counter.
- **Provides a Dedicated Index Word:** The custom word `TI` (for "times index") is used to access the current counter without conflicting with `I`.

---

## Implementation

Below is an example showing the fast loop in action.

```
```

And here is the resulting assembly code.

```
```

---

## Advantages and Trade-offs

### Advantages

- **Lower Instruction Overhead:**  
  Only one parameter is required which makes the construct very efficient.
  
- **Simplicity:**  
  The loop uses a simple countdown; the current iteration is easy to understand and use via `TI`.

- **Clarity in Syntax:**  
  The dedicated keywords (`TIMES` and `NEXT`) clearly distinguish this fast loop from the standard DO/LOOP.

### Trade-offs

- **Non-Standard:**  
  This construct is not defined in ANS Forth, so its use reduces portability.
  
- **Different Semantics:**  
  The standard loop's `I` returns an absolute index. Here, `TI` returns the remaining count (from \( n \) decreasing to 0), which may require adjustment in the loop body if an absolute index is necessary.

---

## Conclusion

The `TIMES ... NEXT` loop offers a lightweight, efficient loop alternative for scenarios where the full generality of DO/LOOP is unnecessary. This approach is especially useful in performance-critical applications where minimal instruction overhead is desired. It provides clear syntax and a dedicated loop counter (`TI`) while preserving the standard DO/LOOP for cases requiring absolute indexing.

Happy looping!