// Core stack manipulation words
macro: dup ( a -- a a ) T[T->N,d+1] endmacro
macro: drop ( a -- ) N[d-1] endmacro
macro: noop ( -- ) T[d+0] endmacro

// :: swap      N     T->N              alu ;
macro: swap ( a b -- b a ) N[T->N] endmacro

// :: over      N     T->N          d+1 alu ;
macro: over ( a b -- a b a ) N[T->N,d+1] endmacro
