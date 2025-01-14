// Test Basic elided words
include "core/j1_base_macros.asm"

start:
    #5 #3        // Stack: 5 3
    2dupand      // Stack: 5 3 1
    drop         // Stack: 5 3
    2dup<        // Stack: 5 3 0
    drop         // Stack: 5 3
    2dup=        // Stack: 5 3 0
    drop         // Stack: 5 3
    2dupor       // Stack: 5 3 7
    drop         // Stack: 5 3
    2dup+        // Stack: 5 3 8
    drop         // Stack: 5 3
    2dup-        // Stack: 5 3 2
    drop         // Stack: 5 3
    2dupu<       // Stack: 5 3 0
    drop         // Stack: 5 3
    2dupxor      // Stack: 5 3 6
    drop         // Stack: 5 3

done:
    noop
    JMP done