// J1 Dual-Port Memory Operation Macros
// These are operations specific to dual-port memory variants

// Memory operations
macro: @       ( addr -- x )           mem[T] endmacro
macro: !       ( x addr -- )           3OS[N->[T],d-2] endmacro
macro: dup@    ( addr -- addr x )      mem[T][T->N,d+1] endmacro
macro: tuck!   ( x addr -- )           T[N->[T],d-1] endmacro
macro: tuckio! ( x addr -- )           T[N->io[T],d-1] endmacro
macro: 2dup!   ( x addr -- x addr )    T[N->[T]] endmacro
macro: 2dupio! ( x addr -- x addr )    T[N->io[T]] endmacro
macro: !r>     ( addr R: x -- )        rT[N->[T],r-1,d-1] endmacro
macro: io!r>   ( addr R: x -- )        rT[N->io[T],r-1,d-1] endmacro

// Stack and memory combinations
macro: dropdup ( a b -- b b )          N endmacro
macro: dropr@  ( a -- r )              rT endmacro
macro: dropr>  ( a -- r R: r -- )      rT[r-1] endmacro
macro: droprdrop ( a -- R: r -- )      N[r-1,d-1] endmacro
macro: niprdrop ( a b -- b R: r -- )   T[r-1,d-1] endmacro

// 3OS optimized operations
macro: 2drop   ( a b -- )              3OS[d-2] endmacro
macro: 2droprdrop ( a b -- R: x -- )   3OS[r-1,d-2] endmacro
macro: 3rd     ( a b c -- a b c a )    3OS[T->N,d+1] endmacro
