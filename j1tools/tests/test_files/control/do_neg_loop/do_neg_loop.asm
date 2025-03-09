ORG $0000
JMP start

include "core/j1_base_macros.asm"

: start
    // First loop: count down from 10 to 0 by -2s
    #0              // Push limit (0)
    #10             // Push initial index (10)
    DO
        // Loop body - just a noop for this basic test
        noop        // Do nothing in the loop body
        #2 neg      // Push 2 and negate it to get -2
    +LOOP           // Add increment to index and continue if > limit
    
    // Second loop: count down from 5 to -5 by -1s
    #5 neg          // Push 5 and negate it to get -5 (limit)
    #5              // Push initial index (5)
    DO
        noop        // Do nothing in the loop body
        #1 neg      // Push 1 and negate it to get -1
    +LOOP           // Add increment to index and continue if > limit
    
: wait_forever
     noop
     JMP wait_forever