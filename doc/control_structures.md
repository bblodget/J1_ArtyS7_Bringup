# Control Structures in the J1 Assembler

This document summarizes the Forth-style control structures supported by the J1 assembler. These structures allow you to express conditional execution and loops while hiding the complexity of label generation and backpatching.

---

## Conditional Branching

### IF THEN

- **Grammar Rule:**  
  ```
  if_then: IF block THEN
  ```

- **Transformation:**  
  ```forth
  // Source Forth:
  IF              ; Condition expected on stack
      block       ; Execute if condition is true
  THEN
  next_instr

  // Transforms into:
  ZJMP if_false   ; Jump to false label if condition is false
  block           ; Block instructions
  +if_false:      ; Target for condition == false
  next_instr
  ```

- **Behavior:**  
  The block is executed only if the condition (expected to be on top of the data stack) is true. Otherwise, execution skips to after the `THEN` keyword. The assembler generates a conditional jump (`ZJMP`) whose target label is backpatched during the second pass.

- **Example:**
  ```forth
  dup #0 > IF
      drop       // Execute if condition is true
  THEN
  ```

### IF ELSE THEN

- **Grammar Rule:**  
  ```
  if_else_then: IF block ELSE block THEN
  ```

- **Transformation:**  
  ```forth
  // Source Forth:
  IF
      true_block      ; Execute if condition is true
  ELSE
      false_block     ; Execute if condition is false
  THEN
  next_instr

  // Transforms into:
  ZJMP if_false      ; Jump to false block if condition is false
  true_block         ; Execute if condition was true
  JMP if_end         ; Skip over false block
  +if_false:         ; Target for condition == false
  false_block        ; Execute if condition was false
  +if_end:           ; Continue with next instruction
  next_instr
  ```

- **Behavior:**  
  If the condition is true, the true_block executes; if it is false, the false_block executes. Two jump instructions are generated: one (ZJMP) to exit the true block and one (JMP) to skip over the false block after executing the true branch.

- **Example:**
  ```forth
  dup #0 > IF
      drop       // True branch
  ELSE
      noop       // False branch
  THEN
  ```

---

## Loop Structures

### BEGIN WHILE REPEAT

- **Grammar Rule:**  
  ```
  loop_while: BEGIN block WHILE block REPEAT
  ```

- **Transformation:**  
  ```forth
  // Source Forth:
  BEGIN
      block1          ; First block executes unconditionally
  WHILE              ; Block1 leaves test condition on stack
      block2          ; Second block executes if condition is true
  REPEAT             ; Jump back to BEGIN
  next_instr

  // Transforms into:
  +begin_label:
  block1             ; First block code
  ZJMP exit_label    ; If condition is false, exit loop
  block2             ; Second block code
  JMP begin_label    ; Jump back to start unconditionally
  +exit_label:       ; Target for condition == false
  next_instr
  ```

- **Behavior:**  
  1. Execution starts at `BEGIN` and executes block1.
  2. A condition is then tested (typically by leaving a flag on the data stack) using the `WHILE` keyword.
  3. If the condition is false, a `ZJMP` exits the loop.
  4. If true, block2 executes, and an unconditional `JMP` sends execution back to the `BEGIN` label.
  5. An exit label is generated following block2 as the target for the `ZJMP`.

- **Example:**
  ```forth
  #5              // Initialize counter with 5

  BEGIN
      dup         // Duplicate counter for condition test
      #0 >        // Test if counter > 0 (implemented as: push 0, then use '>' macro)
  WHILE
      #1 -        // Decrement counter
  REPEAT

  drop           // Clean up the final counter value
  ```

  *Notes:*  
  - Under the hood, the `>` macro is implemented as `swap <` so that it uses the available `<` operation.  
  - The assembler automatically assigns and resolves labels (`begin_x` and `exit_x`) for proper jump targets.

### BEGIN UNTIL

- **Grammar Rule:**  
  ```
  loop_until: BEGIN block UNTIL
  ```

- **Transformation:**  
  ```forth
  // Source Forth:
  BEGIN
      block           ; Block leaves test condition on stack
  UNTIL              ; Loop continues while condition is false
  next_instr

  // Transforms into:
  +begin_label:
  block              ; Block code, leaves condition on stack
  ZJMP begin_label   ; Jump back to begin if condition is false
  next_instr
  ```

- **Behavior:**  
  The loop continues until the condition becomes true. The block is executed, and at the end of the block, a condition is evaluated. If the condition is false, a backward jump continues the loop; if true, execution falls through to the next instruction.

- **Usage Consideration:**  
  Although the typical usage of UNTIL is less common in some languages, it is supported for programs where looping should continue until a specific condition is met.  
  (This structure is similar to a "do-until" loop within the constraints of Forth semantics.)

---

## Implementation Details

- **Label Management:**  
  The assembler uses a two-pass system to collect label references and backpatch jump instructions. This ensures that forward and backward jumps resolve correctly.

- **Stack Effects:**  
  Each control structure respects the stack effect conventions of Forth. For example, the condition for an IF or a loop must leave a flag on the data stack.

- **Macros:**  
  Comparison macros such as `>` and `u>` have been added to improve readability. These are implemented in terms of existing instructions:
  - `>` is defined as `swap <`
  - `u>` is defined as `swap u<`

- **Error Handling:**  
  If a control structure is misused (for example, a block is empty when it shouldn't be), the assembler will raise an error with appropriate line and column information.

---

## Summary

The J1 assembler currently supports the following control structures:
- **Conditional:** `IF THEN`, `IF ELSE THEN`
- **Looping:** `BEGIN WHILE REPEAT` and `BEGIN UNTIL`

These structures allow developers to write high-level control flow logic in Forth style while abstracting away the details of jump instructions and label management. Use them to build robust, readable, and efficient assembly programs for the J1 CPU.

---

*End of Control Structures Documentation*
