// Math operations built from core words
include "core_words.asm"

macro: 2dup ( a b -- a b a b )
    over
    over
endmacro

macro: plus ( a b -- c )
    T+N[d-1]  // ALU add operation (T+N)
endmacro
