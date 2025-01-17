// Macro's for basic forth words

macro: dup ( a -- a a ) T[T->N,d+1] ;
macro: drop ( a -- ) N[d-1] ;
macro: noop ( -- ) T[d+0] ;

