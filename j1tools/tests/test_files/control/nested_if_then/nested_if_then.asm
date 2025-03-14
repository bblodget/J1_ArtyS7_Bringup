ORG $0000
JMP 'start

include "core/j1_base_macros.asm"

: start
    // Test nested IF THEN with a true outer condition.
    1              // Outer condition: true.
    IF
        // Nested IF block: true condition.
        1          // Inner condition (true).
        IF
            dup   // This duplicative operation should run.
        THEN

        // Nested IF block: false condition.
        0          // Inner condition (false).
        IF
            dup   // This code should NOT execute.
        THEN

        drop        // Clean up by dropping the value from the first inner IF.
    THEN
    drop            // Clean up the outer condition.

    // Test simple IF THEN with a false condition.
    0              // Outer condition: false.
    IF
        dup       // This code should NOT execute.
    THEN
    drop            // Drop the false condition.

: wait_forever
     noop
     JMP 'wait_forever

