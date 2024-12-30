# J1 High-Level Assembly Reference

This document describes the high-level operations built into the J1 assembler. These operations are fundamental parts of the assembly language, not macros, and map directly to one or more low-level instructions described in low_level_asm.md.

## Stack Manipulation Words

### Basic Stack Operations
```
DUP     ( n -- n n )         ; Duplicate top of stack
        ; Maps to: T[T->N,d+1]        ; 6011

DROP    ( n -- )             ; Discard top of stack
        ; Maps to: N[d-1]            ; 6103

SWAP    ( n1 n2 -- n2 n1 )  ; Exchange top two items
        ; Maps to: N[T->N]           ; 6112

OVER    ( n1 n2 -- n1 n2 n1 ) ; Copy second item to top
        ; Maps to: N[T->N,d+1]       ; 6111

NIP     ( n1 n2 -- n2 )      ; Drop second item
        ; Maps to: T[d-1]            ; 6003

NOOP    ( -- )               ; No operation
        ; Maps to: T                 ; 6000
```

### Return Stack Operations
```
>R      ( n -- ) (R: -- n)  ; Move to return stack
        ; Maps to: T[T->R,d-1,r+1]   ; 6027

R>      ( -- n ) (R: n -- ) ; Move from return stack
        ; Maps to: rT[d+1,r-1]       ; 6B0D

R@      ( -- n ) (R: n -- n) ; Copy from return stack
        ; Maps to: rT[d+1]           ; 6B01
```

## Arithmetic/Logic Words
```
+       ( n1 n2 -- sum )     ; Add
        ; Maps to: T+N[d-1]          ; 6203
        ; With +RET: T+N[RET,d-1,r-1] ; 628B

-       ( n1 n2 -- diff )    ; Subtract
        ; Maps to: T-N[d-1]          ; 6C03
        ; With +RET: T-N[RET,d-1,r-1] ; 6C8B

1+      ( n -- n+1 )         ; Increment
        ; Maps to: T+1               ; 7600
        ; With +RET: T+1[RET,r-1]    ; 7688

1-      ( n -- n-1 )         ; Decrement
        ; Maps to: T-1               ; 7700
        ; With +RET: T-1[RET,r-1]    ; 7788

2*      ( n -- n*2 )         ; Left shift by 1
        ; Maps to: T2*               ; 6A00
        ; With +RET: T2*[RET,r-1]    ; 6A88

2/      ( n -- n/2 )         ; Right shift by 1
        ; Maps to: T2/               ; 6900
        ; With +RET: T2/[RET,r-1]    ; 6988

AND     ( n1 n2 -- n3 )      ; Bitwise AND
        ; Maps to: T&N[d-1]          ; 6303
        ; With +RET: T&N[RET,d-1,r-1] ; 638B

OR      ( n1 n2 -- n3 )      ; Bitwise OR
        ; Maps to: T|N[d-1]          ; 6403
        ; With +RET: T|N[RET,d-1,r-1] ; 648B

XOR     ( n1 n2 -- n3 )      ; Bitwise XOR
        ; Maps to: T^N[d-1]          ; 6503
        ; With +RET: T^N[RET,d-1,r-1] ; 658B

INVERT  ( n1 -- n2 )         ; Bitwise NOT
        ; Maps to: ~T                 ; 6600
        ; With +RET: ~T[RET,r-1]     ; 6688
```

## Comparison Words
```
=       ( n1 n2 -- flag )    ; Equal
        ; Maps to: N==T[d-1]         ; 6703
        ; With +RET: N==T[RET,d-1,r-1] ; 678B

<       ( n1 n2 -- flag )    ; Less than (signed)
        ; Maps to: N<T[d-1]          ; 6803
        ; With +RET: N<T[RET,d-1,r-1] ; 688B

U<      ( n1 n2 -- flag )    ; Less than (unsigned)
        ; Maps to: Nu<T[d-1]         ; 6F03
        ; With +RET: Nu<T[RET,d-1,r-1] ; 6F8B
```

## Memory/IO Operations
```
@       ( addr -- n )        ; Fetch from memory
        ; Maps to: T[T->N]           ; 6010
        ; With +RET: T[T->N,RET,r-1] ; 6098

!       ( n addr -- )        ; Store to memory
        ; Maps to: T[N->[T],d-2]     ; 6032
        ; With +RET: T[N->[T],RET,d-2,r-1] ; 60BA

IO@     ( port -- n )        ; Input from I/O port
        ; Maps to: io[T],IORD        ; 6D50
        ; With +RET: io[T],IORD[RET,r-1] ; 6DD8

IO!     ( n port -- )        ; Output to I/O port
        ; Maps to: T[N->io[T],d-2]   ; 6042
        ; With +RET: T[N->io[T],RET,d-2,r-1] ; 60CA
```

## System Control Words
```
DINT    ( -- )               ; Disable interrupts
        ; Maps to: T,fDINT           ; 6060

EINT    ( -- )               ; Enable interrupts
        ; Maps to: T,fEINT           ; 6070

DEPTH   ( -- n )             ; Get data stack depth
        ; Maps to: status,T->N,d+1   ; 6E11

RDEPTH  ( -- n )             ; Get return stack depth
        ; Maps to: rstatus,T->N,d+1  ; 7311
```

## Return Optimization

Some high-level words support the "+RET" suffix which combines the operation with a subroutine return. This optimization produces more efficient code by merging the operation with the return instruction.

For example:
```
; Without optimization
square1:
    DUP             ; Duplicate number
    *               ; Multiply
    RET             ; Return (separate instruction)

; With optimization
square2:
    DUP             ; Duplicate number
    *+RET           ; Multiply and return (single instruction)
```

The +RET suffix is only allowed on operations that can be safely combined with a return. These include:
- Arithmetic operations (+, -, *, etc.)
- Logic operations (AND, OR, XOR, INVERT)
- Memory operations (@ and !)

Stack manipulation words like DUP, DROP, SWAP, and OVER do not support +RET as they typically need to maintain specific stack effects.

## Control Flow

### IF THEN Structure
```
IF     ( f -- )     ; Begin conditional
        ; Maps to: ZJMP <THEN_address>  ; 1xxx - Conditional jump
  ...               ; Code executed if flag is true
THEN               ; End conditional
```

### IF ELSE THEN Structure
```
IF     ( f -- )     ; Begin conditional
        ; Maps to: ZJMP <ELSE_address>  ; 1xxx - Jump to ELSE if false
  ...               ; Code executed if flag is true
ELSE               ; 
        ; Maps to: JMP <THEN_address>   ; 0xxx - Unconditional jump
  ...               ; Code executed if flag is false
THEN               ; End conditional
```

### BEGIN UNTIL Structure
```
BEGIN              ; Begin loop
  ...               ; Loop body
UNTIL  ( f -- )     ; End loop, repeat if flag is false
        ; Maps to: ZJMP <BEGIN_address> ; 1xxx - Jump back if false
```

### BEGIN WHILE REPEAT Structure
```
BEGIN              ; Begin loop
  ...               ; Code executed before test
WHILE  ( f -- )     ; If flag is true, continue loop
        ; Maps to: ZJMP <REPEAT_address> ; 1xxx - Exit if false
  ...               ; Code executed if flag was true
REPEAT             ; End loop, jump back to BEGIN
        ; Maps to: JMP <BEGIN_address>   ; 0xxx - Unconditional jump
```

## Examples

### Fibonacci Sequence
```
; Calculate nth Fibonacci number ( n -- fib(n) )
; Example: 7 -> 13 (0,1,1,2,3,5,8,13)
fib:
    DUP             ; n n
    LIT #2          ; n n 2
    U<              ; n (n<2)?
    ZJMP recur      ; Jump if not base case
    DROP            ; Return n for n < 2
    RET

recur:
    DUP             ; n n
    LIT #1          ; n n 1
    -               ; n n-1
    >R              ; n        (R: n-1)
    LIT #2          ; n 2
    -               ; n-2      (R: n-1)
    CALL fib        ; fib(n-2) (R: n-1)
    R>              ; fib(n-2) n-1
    CALL fib        ; fib(n-2) fib(n-1)
    ++RET           ; fib(n-2)+fib(n-1)
```

### Absolute Value
```
; Get absolute value ( n -- |n| )
abs:
    DUP             ; Duplicate number
    LIT #0          ; Push 0
    N<T             ; Compare n < 0
    ZJMP pos        ; Skip negate if n >= 0
    INVERT          ; Bitwise NOT
    1+              ; Add 1 (two's complement negation)
pos:
    RET             ; Return
```

### Countdown
```
; Count down from n to 0, leaving 0 on stack ( n -- 0 )
; Example: 5 -> prints 5,4,3,2,1 and leaves 0 on stack
countdown:
    BEGIN
        DUP         ; n n
        ZJMP done   ; Exit if zero
        DUP         ; n n
        LIT #1      ; Write to output port 1
        IO!         ; (prints number)
        LIT #1      ; n 1
        -           ; n-1
    UNTIL
done:
    RET
```
