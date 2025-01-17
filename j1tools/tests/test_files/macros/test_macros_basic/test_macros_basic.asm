// Simple test program using macros
// Pushes two numbers and adds them
// Uses a macro instead of a subroutine

macro: add_nums ( a b -- sum ) // Stack effect comment shows inputs and outputs
    T+N[d-1]                   // Add top two stack items
    T[T->R,r+1]                // Save result to return stack (push, don't overwrite)
    T[r-1]                     // Pop (return stack) our saved value to T
;

start:                         // Note the colon after label
    #$2A #10                   // Push hex 2A (decimal 42) and decimal 10
    add_nums                   // Use our addition macro
    JMP wait_forever           // Jump to end of program

wait_forever:
    T[d+0]                     // NOOP
    JMP wait_forever           // Loop forever
