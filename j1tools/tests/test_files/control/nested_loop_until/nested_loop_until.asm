ORG #$0000
JMP start

include "core/j1_base_macros.asm"

: start
    // Initialize outer counter
    #3              // Push outer loop counter (3)

    // Outer loop
    BEGIN
        // Initialize inner counter
        #4          // Push inner loop counter (4)
        
        // Inner loop
        BEGIN
            #1 -    // Decrement inner counter
            dup     // Duplicate for test condition
        UNTIL      // Inner loop continues while non-zero
        
        drop       // Clean up inner loop's zero
        
        #1 -       // Decrement outer counter
        dup        // Duplicate for test condition
    UNTIL         // Outer loop continues while non-zero
    
    drop          // Clean up outer loop's zero

: wait_forever
     noop
     JMP wait_forever

