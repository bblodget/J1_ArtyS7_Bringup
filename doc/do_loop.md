# DO LOOP Implementation Plan

## Overview
The DO LOOP structure is a definite loop construct in Forth that provides indexed iteration with support for early exit and nested loops.

## Basic Syntax
```forth
limit index DO
    ... loop body ...
LOOP
```

## Variants
1. Standard LOOP (increment by 1)
```forth
10 0 DO
    i .    \ Print numbers 0 to 9
LOOP
```

2. +LOOP (custom increment)
```forth
10 0 DO
    i .    \ Print with custom step
    2      \ Step by 2
+LOOP      \ Prints 0,2,4,6,8
```

3. LEAVE (early exit)
```forth
10 0 DO
    i 5 = IF
        LEAVE  \ Exit when i equals 5
    THEN
    i .
LOOP
```

## Implementation Components

### 1. Grammar Updates
```lark
// Add to control structure rules
?control_structure: if_then | if_else_then | loop_until | loop_while | do_loop

// DO LOOP specific rules
do_loop: DO block (LOOP | PLUS_LOOP)
LEAVE.2: "LEAVE"
DO.2: "DO"
LOOP.2: "LOOP"
PLUS_LOOP.2: "+LOOP"
```

### 2. Loop Index Access
Implemented as macros in stdlib with compile-time warning support:
```forth
\ loop.fs
\ Loop index words - ONLY use these inside DO LOOP structures
\ The assembler will issue warnings if these are used outside a DO LOOP

macro: i ( -- n )    \ Get innermost loop index
    r@ ;

macro: j ( -- n )    \ Get next-outer loop index
    r> r> r@ >r >r ;

macro: k ( -- n )    \ Get third-level loop index
    r> r> r> r> r@ >r >r >r >r ;
```

The assembler tracks DO LOOP context using the DO and LOOP operations:
```python
def do_op(self, items):
    """Process DO operation and enter loop context."""
    self._do_loop_depth += 1
    self._in_do_loop = True
    # ... process DO operation ...

def loop_op(self, items):
    """Process LOOP operation and exit loop context."""
    # ... process LOOP operation ...
    self._do_loop_depth -= 1
    if self._do_loop_depth == 0:
        self._in_do_loop = False

def call_expr(self, items):
    """Process word calls with loop context checking."""
    name = str(items[0])
    if name in ['i', 'j', 'k']:
        if not self._in_do_loop:
            self.logger.warning(
                f"{self.current_file}:{items[0].line}:{items[0].column}: "
                f"'{name}' used outside DO LOOP"
            )
        elif name == 'j' and self._do_loop_depth < 2:
            self.logger.warning(
                f"{self.current_file}:{items[0].line}:{items[0].column}: "
                f"'j' used in non-nested DO LOOP"
            )
        elif name == 'k' and self._do_loop_depth < 3:
            self.logger.warning(
                f"{self.current_file}:{items[0].line}:{items[0].column}: "
                f"'k' used in insufficiently nested DO LOOP (depth: {self._do_loop_depth})"
            )
```

This approach:
1. Tracks loop context at the token level using separate rules for DO and LOOP
2. Maintains proper nesting depth for nested loops
3. Provides appropriate warnings for:
   - Index words used outside any loop
   - j used without proper nesting (depth < 2)
   - k used without proper nesting (depth < 3)
4. Includes file, line, and column information in warnings
```

Stack Effects for Index Words:
1. `i` ( -- n )
   - Returns innermost loop index
   - Must be used inside a DO LOOP

2. `j` ( -- n )
   - Returns next-outer loop index
   - Must be used inside a nested DO LOOP
   - Warning if not in nested loop context

3. `k` ( -- n )
   - Returns third-level loop index
   - Must be used inside a triply-nested DO LOOP
   - Warning if nesting level < 3

### 3. Code Generation
Basic DO LOOP transforms into:
```forth
\ Source:
10 0 DO     \ limit=10, index=0
   block    \ Loop body
LOOP

\ Transforms to:
>r          \ Save index (0) to R stack
>r          \ Save limit (10) to R stack
+do_label:  \ Start of loop
block       \ Execute loop body
r>          \ Get limit
r>          \ Get index
1+          \ Increment index
2dup        \ Duplicate both for comparison
<           \ Compare index < limit
>r          \ Save new index back
>r          \ Save limit back
ZJMP do_label  \ Jump if index < limit
drop        \ Clean up extra copy of index
drop        \ Clean up extra copy of limit
```

### 4. Stack Effects
1. Before DO:
   - Data stack: ( limit index -- )
   - Return stack: ( -- )

2. During loop:
   - Data stack: ( -- )
   - Return stack: ( -- index limit )

3. After LOOP/+LOOP:
   - Data stack: ( -- )
   - Return stack: ( -- )

### 5. Implementation Phases

1. **Phase 1: Basic Structure**
   - Add grammar rules
   - Implement basic DO LOOP transformation
   - Add loop index macros
   - Basic test cases

2. **Phase 2: +LOOP Extension**
   - Add +LOOP grammar
   - Implement custom increment logic
   - Test positive and negative increments

3. **Phase 3: LEAVE Support**
   - Add LEAVE grammar
   - Implement early exit mechanism
   - Track loop end labels
   - Test LEAVE functionality

4. **Phase 4: Nested Loops**
   - Implement loop nesting tracking
   - Add j and k index support
   - Test nested loop scenarios
   - Add nesting level warnings

5. **Phase 5: Optimization & Validation**
   - Stack effect validation
   - Optimize generated code
   - Warning system for misuse
   - Documentation updates

### 6. Testing Strategy

1. **Basic Tests**
   - Simple counting loops
   - Stack effect verification
   - Index access (i)

2. **+LOOP Tests**
   - Positive increments
   - Negative increments
   - Variable increments

3. **LEAVE Tests**
   - Early exit scenarios
   - Stack cleanup verification
   - Conditional LEAVE

4. **Nesting Tests**
   - Double nested loops
   - Triple nested loops
   - Index access (i, j, k)
   - Mixed with other control structures

5. **Error Cases**
   - Index word usage outside loops
   - Invalid nesting
   - Stack underflow conditions

## Next Steps
1. Begin with grammar updates
2. Implement basic DO LOOP transformation
3. Add loop index macros
4. Create initial test suite