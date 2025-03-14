ORG $0000
JMP 'start

include "core/j1_base_macros.asm"

: start
    // Test IF with a true condition.
    1              // Push a nonzero (true) condition.
    IF
        dup       // This duplicative operation should run.
    THEN
    drop           // Clean up by dropping the duplicate.

    // Test IF with a false condition.
    0              // Push zero (false) condition.
    IF
        dup       // This code should NOT execute.
    THEN
    drop           // Drop the false condition.

: wait_forever
     noop
     JMP 'wait_forever

