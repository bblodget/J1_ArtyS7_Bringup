# J1 Assembly Language Reference

## Comments
Comments start with semicolon and continue to end of line:
```
; This is a comment
```

## Basic Stack Operations
```
NOP                  ; T                    ; 6000 - No operation
DUP                  ; T T->N d+1          ; 6001 - Duplicate top of stack
DROP                 ; N d-1               ; 6003 - Remove top of stack
OVER                ; N T->N d+1          ; 6101 - Copy second item to top
SWAP                ; N T->N              ; 6111 - Exchange top two items
```

## Stack Manipulation
```
>R                   ; N T->R r+1 d-1      ; 6024 - Move to return stack
R>                   ; rT T->N r-1 d+1     ; 6B01 - Move from return stack
R@                   ; rT T->N d+1         ; 6B01 - Copy from return stack
DEPTH               ; status T->N d+1      ; 6E01 - Get stack depth
RDEPTH              ; rstatus T->N d+1     ; 6F01 - Get return stack depth
```

## Memory Operations
```
@                    ; mem[T]              ; 6900 - Fetch from memory
!                    ; N->[T] d-2          ; 6032 - Store to memory
```

## I/O Operations
```
IO@                  ; io[T] IORD          ; 6D50 - Read from I/O port
IO!                  ; N->io[T] d-2        ; 6042 - Write to I/O port
```

## Arithmetic & Logic
```
+                    ; T+N d-1             ; 6203 - Add
-                    ; N-T d-1             ; 6C03 - Subtract
AND                  ; T&N d-1             ; 6303 - Bitwise AND
OR                   ; T|N d-1             ; 6403 - Bitwise OR
XOR                  ; T^N d-1             ; 6503 - Bitwise XOR
INVERT               ; ~T                  ; 6600 - Bitwise NOT
LSHIFT               ; NlshiftT d-1        ; 6A03 - Left shift
RSHIFT               ; NrshiftT d-1        ; 6903 - Right shift
ARSHIFT              ; NarshiftT d-1       ; 6903 - Arithmetic right shift
1+                   ; T+1                 ; 6160 - Increment
1-                   ; T-1                 ; 6170 - Decrement
```

## Comparison
```
=                    ; N==T d-1            ; 6703 - Equal
<                    ; N<T d-1             ; 6803 - Signed less than
U<                   ; Nu<T d-1            ; 6F03 - Unsigned less than
```

## Control Flow
```
JMP label           ; 0xxx - Jump to label (xxx = address)
CALL label          ; 2xxx - Call subroutine (xxx = address)
0BRANCH label       ; 4xxx - Jump if TOS = 0 (xxx = address)
```

## Immediate Values
```
LIT #value          ; 8xxx - Push immediate value (xxx = value)
; Example:
LIT #4000           ; 9000 - Push 0x4000
```

## Labels
```
label:              ; Define a label
    JMP label       ; Jump to label
```

## Interrupt Control
```
DINT                ; 6060 - Disable interrupts
EINT                ; 6070 - Enable interrupts
```

## Example Program
```
; Print 'A' to UART once
start:
    LIT #41         ; 8041 - Push ASCII 'A'
    LIT #1000       ; 9000 - Push UART address
    IO!             ; 6042 - Write and consume both values
    JMP start       ; 0003 - Jump to self (word address 3)
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

