// Test some common Forth words implemented as macros

macro: dup ( a -- a a ) T[T->N,d+1] endmacro
macro: drop ( a -- ) N[d-1]         endmacro
macro: noop ( -- ) T[d+0]           endmacro


: start                         // Note the colon after label
    #42 #10
    dup
    drop
    JMP 'wait_forever           // Jump to end of program

: wait_forever
    noop            
    JMP 'wait_forever           // Loop forever
