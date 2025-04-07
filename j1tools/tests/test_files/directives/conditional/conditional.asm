// Test conditional assembly directives

// ORG $0000
// JMP 'main

// include "core/j1_base_macros.asm"

: main
    // Define some test constants
    .define TEST_CONST 42
    .define ANOTHER_CONST 100

    // Test .if with equality expressions
: positive_test
    .if TEST_CONST == 42
        // This should be assembled
        42
        JMP 'negative_test
    .endif

    0

: negative_test
    .if TEST_CONST == 43
        // This should not be assembled
        43
        JMP 'wait_forever
    .endif

    0

: wait_forever
//    noop
    JMP 'wait_forever
