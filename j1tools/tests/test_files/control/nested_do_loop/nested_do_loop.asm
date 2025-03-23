ORG $0000
JMP 'start

include "core/j1_base_macros.asm"

: start
    // Outer loop: 0 to 2
    3              // Push limit (3)
    0              // Push initial index (0)
    DO
        // Middle loop: 0 to 1
        2          // Push limit (2)
        0          // Push initial index (0)
        DO
            // Inner loop: 0 to 3
            4      // Push limit (4)
            0      // Push initial index (0)
            DO
                // Access loop indices
                k               // Get K outer loop index (0,1,2)
                drop           // Discard for this test
                j               // Get J middle loop index (0,1)
                drop           // Discard for this test
                i               // Get I inner loop index (0,1,2,3)
                drop           // Discard for this test
                noop           // Do nothing else in loop body
            LOOP
        LOOP
    LOOP
    
: wait_forever
     noop
     JMP 'wait_forever

