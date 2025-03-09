ORG $0000
JMP 'start

include "core/j1_base_macros.asm"

: start
    // Test IF ELSE THEN with a true condition.
    #1              // Push a nonzero (true) condition.
    IF
        dup       // This duplicative operation should run.
    ELSE
        drop      // This code should NOT execute.
    THEN
    drop           // Clean up by dropping the duplicate.

    // Test IF ELSE THEN with a false condition.
    #0              // Push zero (false) condition.
    IF
        dup       // This branch should NOT run.
    ELSE
        drop      // This operation should execute.
    THEN
    drop           // Clean up by dropping the condition.

: wait_forever
     noop
     JMP 'wait_forever

