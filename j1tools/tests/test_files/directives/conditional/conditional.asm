// Test conditional assembly directives

// ORG $0000
// JMP 'main

// include "core/j1_base_macros.asm"

: main
    // Define some test constants
    .define TEST_CONST 42
    .define ANOTHER_CONST 100

    // Test .if with equality expressions
    .if TEST_CONST == 42
        // This should be assembled
        1
        JMP 'wait_forever
    .endif

    0

: wait_forever
//    noop
    JMP 'wait_forever
