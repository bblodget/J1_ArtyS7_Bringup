// Test comparison operations
include "core/j1_base_macros.asm"

: start
    // Test comparisons
    10 5       // Stack: 10 5
    u<           // Stack: 0 (false: 10 is not < 5)
    drop         // Stack: empty
    3 8        // Stack: 3 8
    <            // Stack: 1 (true: 3 < 8)
    drop         // Stack: empty
    4 4        // Stack: 4 4
    =            // Stack: 1 (true: 4 = 4)

: done
    noop
    JMP 'done