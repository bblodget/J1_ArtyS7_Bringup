// J1 Extended Operation Macros
// These are operations specific to extended variants (HX8K)

// Shift operations
macro: lshift         ( x n -- x<<n )     NlshiftT[d-1] endmacro
macro: rshift         ( x n -- x>>n )     NrshiftT[d-1] endmacro
macro: arshift        ( x n -- x>>n )     NarshiftT[d-1] endmacro
macro: overswaplshift ( a b -- a b<<a )   NlshiftT endmacro
macro: overswaprshift ( a b -- a b>>a )   NrshiftT endmacro
macro: overswaparshift ( a b -- a b>>a )  NarshiftT endmacro

// Multiply operations
macro: um*low         ( u1 u2 -- ul )     L-UM*[d-1] endmacro
macro: um*high        ( u1 u2 -- uh )     H-UM*[d-1] endmacro
macro: 2dupum*low     ( a b -- a b ul )   L-UM*[T->N,d+1] endmacro
macro: 2dupum*high    ( a b -- a b uh )   H-UM*[T->N,d+1] endmacro

// Increment/Decrement operations
macro: 1+             ( n -- n+1 )        T+1 endmacro
macro: 1-             ( n -- n-1 )        T-1 endmacro
macro: dup1+          ( n -- n n+1 )      T+1[T->N,d+1] endmacro
macro: dup>r1+        ( n -- n+1 R: -- n) T+1[T->R,r+1] endmacro
macro: tuck!1+        ( x addr -- addr+1) T+1[N->[T],d-1] endmacro

// Status operations
macro: rdepth         ( -- n )            rstatus[T->N,d+1] endmacro
