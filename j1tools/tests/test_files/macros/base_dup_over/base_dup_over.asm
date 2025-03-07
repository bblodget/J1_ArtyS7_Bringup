// Test dup>r and over operations
include "core/j1_base_macros.asm"

: start
    #5 #3        // Stack: 5 3
    dup>r        // Stack: 5 3, R: 3
    r>           // Stack: 5 3 3
    drop         // Stack: 5 3
    overand      // Stack: 5 1
    over>        // Stack: 5 0
    over=        // Stack: 5 0
    overor       // Stack: 5 5
    over+        // Stack: 5 10
    overu>       // Stack: 5 FFFF (true, because 10 > 5)
    overxor      // Stack: 5 FFFA (FFFF xor 5 = FFFA)

: done
    noop
    JMP done