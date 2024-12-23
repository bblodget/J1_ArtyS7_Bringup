; Comments start with semicolon
; Basic instructions
NOP                  ; T
DUP                  ; T T->N d+1
DROP                 ; N d-1
OVER                 ; N T->N d+1
SWAP                 ; N T->N

; IO operations
IO@                  ; io[T] IORD
IO!                  ; N->io[T]

; Immediate values (prefixed with #)
LIT #4000            ; Push immediate value 0x4000

; Labels and jumps
start:              ; Define a label
    JMP start       ; Jump to label

