// J1 Base ALU Operation Macros
// These are the fundamental ALU operations present in all J1 variants

// Basic stack operations
macro: noop    ( -- )              T              endmacro
macro: dup     ( a -- a a )        T[T->N,d+1]    endmacro
macro: drop    ( a -- )            N[d-1]         endmacro
macro: swap    ( a b -- b a )      N[T->N]        endmacro
macro: over    ( a b -- a b a )    N[T->N,d+1]    endmacro
macro: nip     ( a b -- b )        T[d-1]         endmacro

// ALU operations
macro: +       ( a b -- c )        T+N[d-1]       endmacro
macro: -       ( a b -- c )        N-T[d-1]       endmacro
macro: and     ( a b -- c )        T&N[d-1]       endmacro
macro: or      ( a b -- c )        T|N[d-1]       endmacro
macro: xor     ( a b -- c )        T^N[d-1]       endmacro
macro: invert  ( a -- ~a )         ~T             endmacro
macro: =       ( a b -- f )        N==T[d-1]      endmacro
macro: <       ( a b -- f )        N<T[d-1]       endmacro
macro: >       ( a b -- f )        swap <        endmacro
macro: u<      ( a b -- f )        Nu<T[d-1]      endmacro
macro: u>      ( a b -- f )        swap u<       endmacro
macro: 2/      ( n -- n/2 )        T2/            endmacro
macro: 2*      ( n -- n*2 )        T2*            endmacro

// Return stack operations
macro: >r      ( a -- R: -- a )    N[T->R,r+1,d-1] endmacro
macro: r>      ( -- a R: a -- )    rT[T->N,r-1,d+1] endmacro
macro: r@      ( -- a R: a -- a )  rT[T->N,d+1]    endmacro
macro: rdrop   ( -- R: a -- )      T[r-1]         endmacro

// I/O operations
macro: io@     ( addr -- val )     io[T][IORD]    endmacro
macro: io!     ( val addr -- )     3OS[N->io[T],d-2] endmacro

// Status and control
macro: depth   ( -- n )            status[T->N,d+1] endmacro
macro: exit    ( R: addr -- )      T[RET,r-1]     endmacro
macro: ;       ( -- )              T[RET,r-1]     endmacro
macro: dint    ( -- )              T[fDINT]       endmacro
macro: eint    ( -- )              T[fEINT]       endmacro

// Basic elided words
macro: 2dupand ( a b -- a b a&b )  T&N[T->N,d+1]  endmacro
macro: 2dup<   ( a b -- a b f )    N<T[T->N,d+1]  endmacro
macro: 2dup=   ( a b -- a b f )    N==T[T->N,d+1] endmacro
macro: 2dupor  ( a b -- a b a|b )  T|N[T->N,d+1]  endmacro
macro: 2dup+   ( a b -- a b sum )  T+N[T->N,d+1]  endmacro
macro: 2dup-   ( a b -- a b dif )  N-T[T->N,d+1]  endmacro
macro: 2dupu<  ( a b -- a b f )    Nu<T[T->N,d+1] endmacro
macro: 2dupxor ( a b -- a b x )    T^N[T->N,d+1]  endmacro
macro: dup>r   ( a -- a R: -- a )  T[T->R,r+1]    endmacro
macro: overand ( a b -- a a&b )    T&N            endmacro
macro: over>   ( a b -- a b>a )    N<T            endmacro
macro: over=   ( a b -- a b=a )    N==T            endmacro
macro: overor  ( a b -- a a|b )    T|N            endmacro
macro: over+   ( a b -- a a+b )    T+N            endmacro
macro: overu>  ( a b -- a b>ua )   Nu<T           endmacro
macro: overxor ( a b -- a a^b )    T^N            endmacro

// Loop index access macros
macro: i     ( -- n )    r@                       endmacro            // Get innermost loop index
macro: j     ( -- n )    r> r> r@ >r >r          endmacro  // Get next-outer loop index
macro: k     ( -- n )    r> r> r> r> r@ >r >r >r >r endmacro  // Get third-level loop index

// Negation operation (two's complement)
macro: neg     ( n -- -n )         ~T T+1[d-1]    endmacro  // Invert and add 1

