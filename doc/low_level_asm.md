# J1 Low-Level Assembly Reference

This document describes the fundamental ALU operations and modifier syntax for direct control of the J1 processor.

## Number Format
Numbers can be specified in decimal or hexadecimal:
```
LIT #42       ; Decimal number
LIT #$2A      ; Hexadecimal number (same as 42)
```
The `#` prefix indicates an immediate value, and `$` prefix indicates hexadecimal format.

## Jump Instructions
```
JMP addr              ; 0000 - Unconditional jump
ZJMP addr            ; 1000 - Jump if TOS = 0 (conditional)
CALL addr            ; 2000 - Call subroutine
```
Note: Addresses are word addresses (not byte addresses). Each word is 16 bits, so:
- Word address 1 = byte address 2
- Word address N = byte address N*2

## ALU Operations

### Basic Stack Access
```
T                    ; 6000 - Copy top of stack
N                    ; 6100 - Copy next on stack (NOS)
```

### Arithmetic Operations
```
T+N                  ; 6200 - Add
T-N                  ; 6C00 - Subtract
1+                   ; 6160 - Increment
1-                   ; 6170 - Decrement
```

### Logic Operations
```
T&N                  ; 6300 - Bitwise AND
T|N                  ; 6400 - Bitwise OR
T^N                  ; 6500 - Bitwise XOR
~T                   ; 6600 - Bitwise NOT
```

### Shift Operations
```
N<<T                 ; 6A00 - Left shift
N>>T                 ; 6900 - Right shift (logical)
N>>>T                ; 6900 - Right shift (arithmetic)
```

### Comparison Operations
```
N==T                 ; 6700 - Equal
N<T                  ; 6800 - Less than (signed)
Nu<T                 ; 6F00 - Less than (unsigned)
```

## Instruction Modifiers
ALU operations can be modified with optional stack and memory operations using the bracket syntax:
```
INSTRUCTION [modifier,modifier,...]
```

### Stack Modifiers
```
Data Stack (d):
d+0      - Data stack unchanged
d+1      - Push to data stack
d-1      - Pop from data stack
d-2      - Pop two from data stack

Return Stack (r):
r+0      - Return stack unchanged
r+1      - Push to return stack
r-1      - Pop from return stack (RET)
r-2      - Pop two from return stack
```

### Memory/Copy Modifiers
```
T->N     - Copy T to N
T->R     - Copy T to R
N->[T]   - Store N to memory[T]
```

## Examples Using Modifiers
```
; Stack manipulation
T[T->N,d+1]         ; Copy T to N and push (like DUP)
N[d-1]              ; Remove T, bring up N (like DROP)

; Memory operations
T[N->[T],d-2]       ; Store N to address T, consume both (like !)

; Return variations
T+N[d-1,r-1]        ; Add, pop data stack, and return
T[T->R,r-1]         ; Copy T to R and return
```

## Custom Instructions
For advanced users, custom instructions can be created using direct bit patterns:
```
CODE #$6203         ; Explicit bit pattern for T+N,d-1 (ALU)
CODE #$2000         ; Call to address 0 (Jump)
BYTE #$62 #$03     ; Same as above, but byte by byte
```

The instruction encoding can represent any valid J1 instruction type:
- Literal (8xxx)
- Jump/Call (0xxx-2xxx)
- ALU (6xxx)

## Instruction Encoding
The J1 ALU instruction format is:
```
15 14 13 12 11 10  9  8  7  6  5  4  3  2  1  0
 0  1  1  a  a  a  a  a  s  s  s  s  r  r  d  d

a: ALU operation
s: Stack/Memory operation
r: Return stack delta
d: Data stack delta
```

### Stack Delta Encoding
```
Return Stack (rr):
00: r+0 (unchanged)    (0x0)
01: r+1 (push)         (0x4)
10: r-2                (0x8)
11: r-1 (pop)          (0xC)

Data Stack (dd):
00: d+0 (unchanged)    (0x0)
01: d+1 (push)         (0x1)
10: d-2                (0x2)
11: d-1 (pop)          (0x3)
```

### Stack/Memory Operations
```
Stack Copy Operations:
T->N     - Copy T to N
T->R     - Copy T to R

Memory Operations:
N->[T]   - Store N to memory[T]

I/O Operations:
N->io[T] - I/O write
IORD     - I/O read

Interrupt Control:
fDINT    - Disable interrupts
fEINT    - Enable interrupts

Special Operations:
RET      - Return from subroutine
```

Each operation occupies bits 7-4 (ssss) in the instruction encoding:
```
0000: No operation
0010: T->N       - Copy T to N
0020: T->R       - Copy T to R
0030: N->[T]     - Memory write
0040: N->io[T]   - I/O write
0050: IORD       - I/O read
0060: fDINT      - Disable interrupts
0070: fEINT      - Enable interrupts
0080: RET        - Return
```

These operations can be combined with ALU operations and stack delta modifiers:
```
T+N[T->R,d-1]     ; Add T and N, copy result to R, pop data stack
T[T->N,d+1]       ; Copy T to N and push (DUP)
N[N->[T],d-2]     ; Store N to memory[T], pop both
```

## Instruction Components

An ALU instruction consists of mutually exclusive options in each field:

### Stack/Memory Operations (bits 7-4, choose one)
```
Stack Copy Operations:
T->N     - Copy T to N
T->R     - Copy T to R

Memory Operations:
N->[T]   - Store N to memory[T]

I/O Operations:
N->io[T] - I/O write
IORD     - I/O read

Interrupt Control:
fDINT    - Disable interrupts
fEINT    - Enable interrupts

Special Operations:
RET      - Return from subroutine
```

### Return Stack Delta (bits 3-2, choose one)
```
r+0      - Return stack unchanged
r+1      - Push to return stack
r-1      - Pop from return stack (RET)
r-2      - Pop two from return stack
```

### Data Stack Delta (bits 1-0, choose one)
```
d+0      - Data stack unchanged
d+1      - Push to data stack
d-1      - Pop from data stack
d-2      - Pop two from data stack
```

## Examples
```
; Each modifier field can have only one option:
T+N[T->N,d-1]       ; Valid: one stack op, one data stack delta
T+N[T->N,T->R]      ; Invalid: two stack operations
T+N[d-1,d+1]        ; Invalid: two data stack deltas
T+N[r-1,r+1]        ; Invalid: two return stack deltas
```