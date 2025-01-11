// Test some common Forth words implemented as macros

// :: dup       T     T->N          d+1 alu ;
macro: dup ( a -- a a ) 
    T[T->N,d+1] 
;

// :: drop      N                   d-1 alu ;
macro: drop ( a -- ) 
    N[d-1] 
;

// :: noop      T                       alu ;
macro: noop ( -- ) 
    T[d+0] 
;


start:                         // Note the colon after label
    #42
    dup
    drop
    JMP wait_forever           // Jump to end of program

wait_forever:
    noop            
    JMP wait_forever           // Loop forever
