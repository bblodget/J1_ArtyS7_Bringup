ORG $0000
JMP start

include "core/j1_base_macros.asm"

: start
    // Initialize counter
    #5              // Push initial counter value

    // Loop while counter is greater than zero
    BEGIN
        dup         // Duplicate counter for test
        #0 >        // Test if counter > 0 (leaves flag for WHILE)
    WHILE
        #1 -        // Decrement counter
    REPEAT
    
    drop           // Clean up the final counter

: wait_forever
     noop
     JMP wait_forever

