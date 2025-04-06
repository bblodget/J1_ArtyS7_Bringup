// Test conditional assembly directives

ORG $0000
JMP 'main

include "core/j1_base_macros.asm"

: main
    // Define some test constants
    .define TEST_CONST 42
    .define ANOTHER_CONST 100

    // Test .if with equality expressions
    .if TEST_CONST == 42
        // This should be assembled
        dup
    .else
        // This should not be assembled
        drop
    .endif

    // Test .ifdef
    .ifdef TEST_CONST
        // This should be assembled
        dup
    .else
        // This should not be assembled
        drop
    .endif

    // Test .ifndef
    .ifndef UNDEFINED_CONST
        // This should be assembled
        dup
    .else
        // This should not be assembled
        drop
    .endif

    // Test nested conditionals with equality
    .if TEST_CONST == 42
        .if ANOTHER_CONST == 100
            // This should be assembled
            dup
        .else
            // This should not be assembled
            drop
        .endif
    .else
        // This should not be assembled
        drop
    .endif 
