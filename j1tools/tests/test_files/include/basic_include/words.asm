// Macro's for basic forth words

macro: dup ( a -- a a ) T[T->N,d+1] endmacro
macro: drop ( a -- ) N[d-1]         endmacro
macro: noop ( -- ) T[d+0]           endmacro

: add_nums                // Note the colon after label
    T+N[d-1]             // Add top two stack items
    T[T->R,r+1]          // Save result to return stack (push, don't overwrite)
    T[r-1]               // Pop our saved value to T
    T[RET,r-1]           // Return to caller

