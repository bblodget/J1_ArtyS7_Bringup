// Test return stack operations
include "core/j1_base_macros.asm"

: start
    // Test return stack operations
    #42          // Stack: 42
    >r           // Stack: empty, R: 42
    #7           // Stack: 7
    >r           // Stack: empty, R: 42 7
    r@           // Stack: 7, R: 42 7
    r>           // Stack: 7 7, R: 42
    =            // Stack: 1 (true: values match)
    r>           // Stack: 1 42, R: empty
    drop         // Stack: 1
    drop         // Stack: empty

: done
    noop
    JMP done