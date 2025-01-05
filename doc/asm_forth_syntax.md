# Forth-like Syntax in J1 Assembly

## Future Enhancement Proposal

The J1 processor is designed to run Forth, so it makes sense to consider adding Forth-like syntax to our assembly language. This would make the assembly code more familiar to Forth programmers and provide clearer documentation of stack effects.

## Proposed Syntax

### Function Definitions
Currently in assembly:
```
test_eq:
    =+RET     ; Compare and return
```

Proposed Forth-style:
```
: test_eq  ( n1 n2 -- flag )  =+RET ;
```

### Optimization Features

#### 1. Macro Definitions
For simple substitutions that should be inlined:
```
macro: equals ( n1 n2 -- flag ) =+RET ;
macro: less_than ( n1 n2 -- flag ) <+RET ;
```

#### 2. Constant Folding
For operations that can be computed at assembly time, the assembler needs built-in knowledge of how to emulate these operations:

```
; These operations require assembler support for emulation
foldable: +    ( n1 n2 -- sum )   ADD+RET ;  ; Assembler must know how to add
foldable: -    ( n1 n2 -- diff )  -+RET ;    ; Assembler must know how to subtract
foldable: and  ( n1 n2 -- n3 )    AND+RET ;  ; Assembler must know how to AND

; Example of constant folding
main:
    #5 #3 +   ; Assembler can fold this to #8
    #7 #2 -   ; Assembler can fold this to #5
```

The assembler must:
1. Maintain a simulation stack during assembly
2. Know how to emulate each foldable operation
3. Replace operations with constants when inputs are known
4. Fall back to normal code generation when values aren't constant

#### 3. Inline Operations
There are two proposed ways to inline code:

a. Using the INLINE directive:
```
double:         ; Define subroutine
    #2 *+RET   ; Double top of stack and return

main:
    CALL double    ; Normal subroutine call
    INLINE double  ; Copies instructions inline
```

b. Using inline: declaration:
```
inline: equals ( n1 n2 -- flag ) =+RET ;
inline: add2 ( n -- n+2 ) #2 + ;
```

The INLINE directive is simpler and works with existing subroutines, while the inline: declaration provides better documentation of stack effects.

### Benefits
1. Stack effect comments `( n1 n2 -- flag )` clearly document inputs and outputs
2. Familiar syntax for Forth programmers
3. More compact representation for simple functions
4. Optimization hints for the assembler
5. Constant folding for compile-time computation
6. Multiple inlining strategies for different use cases

### Implementation Notes
To implement this syntax, the assembler would need to:
1. Support `: name` as an alternative to `name:`
2. Treat `( ... )` as comments for stack effect documentation
3. Ignore the trailing `;`
4. Support optimization directives (`macro:`, `foldable:`, `inline:`)
5. Implement constant folding for compile-time optimization
6. Support INLINE directive for existing subroutines
7. Preserve compatibility with traditional assembly syntax

### Examples
```
; Comparison operations with stack effects and optimizations
macro: =    ( n1 n2 -- flag )  =+RET ;    ; Equal
macro: <    ( n1 n2 -- flag )  <+RET ;    ; Less than (signed)
macro: U<   ( n1 n2 -- flag )  U<+RET ;   ; Less than (unsigned)

; Arithmetic operations with constant folding
foldable: +    ( n1 n2 -- sum )   ADD+RET ;  ; Addition
foldable: -    ( n1 n2 -- diff )  -+RET ;    ; Subtraction
foldable: and  ( n1 n2 -- n3 )    AND+RET ;  ; AND

; Always inline these operations
inline: 2*   ( n -- n2 )    T2* ;           ; Shift left
inline: 2/   ( n -- n2 )    T2/ ;           ; Shift right

; Example of INLINE directive
double:
    #2 *+RET
main:
    INLINE double  ; Inlines the multiply operation
```

This enhancement would maintain the simplicity of our assembler while adding documentation and optimization features from Forth.

## Assembler vs Forth Compiler

While our enhanced J1 assembler uses Forth-like syntax and concepts, it remains fundamentally different from a traditional Forth compiler:

### Traditional Forth Compiler
- Interactive environment with immediate execution
- Runtime dictionary for word lookup
- Dynamic memory allocation
- Immediate and compile-time words
- Full interpreter for interactive development
- Runtime overhead for dictionary searches
- Dynamic word definition and modification

### Our Enhanced J1 Assembler
- Static compilation model
- Macro-based word expansion
- Compile-time only processing
- No runtime dictionary overhead
- All words resolved at assembly time
- Aggressive optimization opportunities
- Direct hardware control

### Key Benefits of Our Approach
1. **Performance**
   - No runtime dictionary lookups
   - Smaller code size
   - No interpretation overhead
   - Direct machine code generation

2. **Optimization**
   - Constant folding at assembly time
   - Macro inlining
   - Dead code elimination
   - Stack effect analysis

3. **Development Experience**
   - Familiar Forth syntax
   - Clear stack effect documentation
   - Rich development tools
   - Detailed error messages

This hybrid approach gives us the readability and expressiveness of Forth while maintaining the efficiency and control of assembly language.
