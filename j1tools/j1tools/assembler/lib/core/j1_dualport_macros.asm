// J1 Dual-Port Memory Operation Macros
// These are operations specific to dual-port memory variants

// Memory operations
macro: @       ( addr -- x )           mem[T] ;
macro: !       ( x addr -- )           3OS[N->[T],d-2] ;
macro: dup@    ( addr -- addr x )      mem[T][T->N,d+1] ;
macro: tuck!   ( x addr -- )           T[N->[T],d-1] ;
macro: tuckio! ( x addr -- )           T[N->io[T],d-1] ;
macro: 2dup!   ( x addr -- x addr )    T[N->[T]] ;
macro: 2dupio! ( x addr -- x addr )    T[N->io[T]] ;
macro: !r>     ( addr R: x -- )        rT[N->[T],r-1,d-1] ;
macro: io!r>   ( addr R: x -- )        rT[N->io[T],r-1,d-1] ;

// Stack and memory combinations
macro: dropdup ( a b -- b b )          N ;
macro: dropr@  ( a -- r )              rT ;
macro: dropr>  ( a -- r R: r -- )      rT[r-1] ;
macro: droprdrop ( a -- R: r -- )      N[r-1,d-1] ;
macro: niprdrop ( a b -- b R: r -- )   T[r-1,d-1] ;

// 3OS optimized operations
macro: 2drop   ( a b -- )              3OS[d-2] ;
macro: 2droprdrop ( a b -- R: x -- )   3OS[r-1,d-2] ;
macro: 3rd     ( a b c -- a b c a )    3OS[T->N,d+1] ;
