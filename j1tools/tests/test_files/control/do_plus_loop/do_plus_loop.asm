ORG $0000
JMP 'start

include "core/j1_base_macros.asm"

: start
    // Initialize loop parameters
    10             // Push limit (10)
    0              // Push initial index (0)

    // Loop from 0 to 9 by 2s
    DO
        // Loop body - just a noop for this basic test
        noop        // Do nothing in the loop body
        2          // Push increment value (2)
    +LOOP           // Add increment to index and continue if < limit
    
: wait_forever
     noop
     JMP 'wait_forever

