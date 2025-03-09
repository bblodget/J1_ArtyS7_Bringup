// Test ALU operations
include "core/j1_base_macros.asm"

: start
    // Test ALU operations
    #8           // Stack: 8
    #5           // Stack: 8 5
    +            // Stack: 13
    #3           // Stack: 13 3
    -            // Stack: 10
    #7           // Stack: 10 7
    and          // Stack: 2
    #5           // Stack: 2 5
    or           // Stack: 7
    #3           // Stack: 7 3
    xor          // Stack: 4
    invert       // Stack: -5 (0xFFFB)

: done
    noop
    JMP 'done