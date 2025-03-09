ORG $0000
JMP start

include "platform/j1_16kb_dualport_macros.asm"

: start
    // Initialize loop parameters
    #3              // Push limit (3)
    #0              // Push initial index (0)

    // Loop from 0 to 4 inclusive
    DO
        // Loop body - just decrement a counter
        noop        // Do nothing in the loop body for this basic test
    LOOP
    
: wait_forever
     noop
     JMP wait_forever

