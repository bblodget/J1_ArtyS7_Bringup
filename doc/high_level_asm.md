# J1 High-Level Assembly Reference

This document describes the high-level operations built into the J1 assembler. These operations are fundamental parts of the assembly language, not macros, and can be modified using the syntax described in low_level_asm.md.

## Stack Manipulation Words

### Basic Stack Operations
```
DUP     ( n -- n n )         ; Duplicate top of stack
        ; Maps to: T[T->N,d+1]        ; 6011 - T->N and d+1

DROP    ( n -- )             ; Discard top of stack
        ; Maps to: N[d-1]            ; 6103 - Copy N and d-1

SWAP    ( n1 n2 -- n2 n1 )  ; Exchange top two items
        ; Maps to: N[T->N]           ; 6112 - N with T->N

OVER    ( n1 n2 -- n1 n2 n1 ) ; Copy second item to top
        ; Maps to: N[T->N,d+1]       ; 6111 - N with T->N and d+1
```

### Return Stack Operations
```
>R      ( n -- ) (R: -- n)  ; Move to return stack
        ; Maps to: T[T->R,d-1,r+1]   ; 6027 - T->R with d-1 and r+1

R>      ( -- n ) (R: n -- ) ; Move from return stack
        ; Maps to: rT[d+1,r-1]       ; 6B0D - rT with d+1 and r-1

R@      ( -- n ) (R: n -- n) ; Copy from return stack
        ; Maps to: rT[d+1]           ; 6B01 - rT with d+1
```

## Arithmetic/Logic Words
```
+       ( n1 n2 -- sum )     ; Add
        ; Maps to: T+N[d-1]          ; 6203 - T+N with d-1

-       ( n1 n2 -- diff )    ; Subtract
        ; Maps to: T-N[d-1]          ; 6C03 - T-N with d-1

AND     ( n1 n2 -- n3 )      ; Bitwise AND
        ; Maps to: T&N[d-1]          ; 6303 - T&N with d-1

OR      ( n1 n2 -- n3 )      ; Bitwise OR
        ; Maps to: T|N[d-1]          ; 6403 - T|N with d-1

XOR     ( n1 n2 -- n3 )      ; Bitwise XOR
        ; Maps to: T^N[d-1]          ; 6503 - T^N with d-1

INVERT  ( n1 -- n2 )         ; Bitwise NOT
        ; Maps to: ~T                 ; 6600 - ~T
```

## Memory Operations
```
@       ( addr -- n )        ; Fetch
        ; Maps to: T[T->N]           ; 6010 - Memory read is implicit

!       ( n addr -- )        ; Store
        ; Maps to: T[N->[T],d-2]     ; 6032 - Store with d-2
```

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

## Using Modifiers

All high-level words accept the same modifiers as their low-level equivalents:

```
DUP[T->R]           ; Duplicate and copy to R
        ; Maps to: T[T->N,T->R,d+1]    ; 6031 - T->N, T->R with d+1

SWAP[r-1]           ; Exchange top two items and return
        ; Maps to: N[T->N,r-1]         ; 611C - N with T->N and r-1

+[T->R,d-1]         ; Add and copy to R
        ; Maps to: T+N[T->R,d-1]       ; 6223 - T+N with T->R and d-1
```

## Examples

### Square a Number
```
; Square the number on top of stack ( n -- n^2 )
square:
    DUP             ; Duplicate number
    *               ; Multiply
    RET             ; Return
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