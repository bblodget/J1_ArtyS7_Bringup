# J1 Assembly Language Reference

## Comments
Comments start with semicolon and continue to end of line:
```
; This is a comment
```

## Basic Stack Operations
```
NOP                  ; T                    ; No operation
DUP                  ; T T->N d+1          ; Duplicate top of stack
DROP                 ; N d-1               ; Remove top of stack
OVER                ; N T->N d+1          ; Copy second item to top
SWAP                ; N T->N              ; Exchange top two items
```

## Stack Manipulation
```
>R                   ; N T->R r+1 d-1      ; Move to return stack
R>                   ; rT T->N r-1 d+1     ; Move from return stack
R@                   ; rT T->N d+1         ; Copy from return stack
DEPTH               ; status T->N d+1      ; Get stack depth
RDEPTH              ; rstatus T->N d+1     ; Get return stack depth
```

## Memory Operations
```
@                    ; mem[T]              ; Fetch from memory
!                    ; N->[T] d-2          ; Store to memory
```

## I/O Operations
```
IO@                  ; io[T] IORD          ; Read from I/O port
IO!                  ; N->io[T] d-2        ; Write to I/O port
```

## Arithmetic & Logic
```
+                    ; T+N d-1             ; Add
-                    ; N-T d-1             ; Subtract
AND                  ; T&N d-1             ; Bitwise AND
OR                   ; T|N d-1             ; Bitwise OR
XOR                  ; T^N d-1             ; Bitwise XOR
INVERT               ; ~T                  ; Bitwise NOT
LSHIFT               ; NlshiftT d-1        ; Left shift
RSHIFT               ; NrshiftT d-1        ; Right shift
ARSHIFT              ; NarshiftT d-1       ; Arithmetic right shift
1+                   ; T+1                 ; Increment
1-                   ; T-1                 ; Decrement
```

## Comparison
```
=                    ; N==T d-1            ; Equal
<                    ; N<T d-1             ; Signed less than
U<                   ; Nu<T d-1            ; Unsigned less than
```

## Control Flow
```
JMP label           ; Jump to label
CALL label          ; Call subroutine
0BRANCH label       ; Jump if TOS = 0
```

## Immediate Values
```
LIT #value          ; Push immediate value
; Example:
LIT #4000           ; Push 0x4000
```

## Labels
```
label:              ; Define a label
    JMP label       ; Jump to label
```

## Interrupt Control
```
DINT                ; Disable interrupts
EINT                ; Enable interrupts
```

## Example Program
```
; Print 'A' to UART once
start:
    LIT #41         ; Push ASCII 'A'
    LIT #1000       ; Push UART address
    IO!             ; Write and consume both values
    JMP start       ; Loop forever
```

## Stack Effects
Stack effects are noted in comments using:
- `d+1`: Push to data stack
- `d-1`: Pop from data stack
- `d-2`: Pop two items from data stack
- `r+1`: Push to return stack
- `r-1`: Pop from return stack
- `T`: Top of stack
- `N`: Next on stack
- `rT`: Top of return stack

