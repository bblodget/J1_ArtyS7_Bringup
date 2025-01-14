// J1 Base ALU Operation Macros
// These are the fundamental ALU operations present in all J1 variants

// Basic stack operations
macro: noop    ( -- )              T ;
macro: dup     ( a -- a a )        T[T->N,d+1] ;
macro: drop    ( a -- )            N[d-1] ;
macro: swap    ( a b -- b a )      N[T->N] ;
macro: over    ( a b -- a b a )    N[T->N,d+1] ;
macro: nip     ( a b -- b )        T[d-1] ;

// ALU operations
macro: +       ( a b -- c )        T+N[d-1] ;
macro: -       ( a b -- c )        N-T[d-1] ;
macro: and     ( a b -- c )        T&N[d-1] ;
macro: or      ( a b -- c )        T|N[d-1] ;
macro: xor     ( a b -- c )        T^N[d-1] ;
macro: invert  ( a -- ~a )         ~T ;
macro: =       ( a b -- f )        N==T[d-1] ;
macro: <       ( a b -- f )        N<T[d-1] ;
macro: u<      ( a b -- f )        Nu<T[d-1] ;
macro: 2/      ( n -- n/2 )        T2/ ;
macro: 2*      ( n -- n*2 )        T2* ;

// Return stack operations
macro: >r      ( a -- R: -- a )    N[T->R,r+1,d-1] ;
macro: r>      ( -- a R: a -- )    rT[T->N,r-1,d+1] ;
macro: r@      ( -- a R: a -- a )  rT[T->N,d+1] ;
macro: rdrop   ( -- R: a -- )      T[r-1] ;

// I/O operations
macro: io@     ( addr -- val )     io[T][IORD] ;
macro: io!     ( val addr -- )     T[N->io[T],d-1] ;

// Status and control
macro: depth   ( -- n )            status[T->N,d+1] ;
macro: exit    ( R: addr -- )      T[RET,r-1] ;
macro: dint    ( -- )              T[fDINT] ;
macro: eint    ( -- )              T[fEINT] ;

// Basic elided words
macro: 2dupand ( a b -- a b a&b )  T&N[T->N,d+1] ;
macro: 2dup<   ( a b -- a b f )    N<T[T->N,d+1] ;
macro: 2dup=   ( a b -- a b f )    N==T[T->N,d+1] ;
macro: 2dupor  ( a b -- a b a|b )  T|N[T->N,d+1] ;
macro: 2dup+   ( a b -- a b sum )  T+N[T->N,d+1] ;
macro: 2dup-   ( a b -- a b dif )  N-T[T->N,d+1] ;
macro: 2dupu<  ( a b -- a b f )    Nu<T[T->N,d+1] ;
macro: 2dupxor ( a b -- a b x )    T^N[T->N,d+1] ;
macro: dup>r   ( a -- a R: -- a )  T[T->R,r+1] ;
macro: overand ( a b -- a a&b )    T&N ;
macro: over>   ( a b -- a b>a )    N<T ;
macro: over=   ( a b -- a b=a )    N==T ;
macro: overor  ( a b -- a a|b )    T|N ;
macro: over+   ( a b -- a a+b )    T+N ;
macro: overu>  ( a b -- a b>ua )   Nu<T ;
macro: overxor ( a b -- a a^b )    T^N ;
