ORG #$0000
JMP start

include "core/j1_base_macros.asm"

start:
    // Initialize counter
    #5              // Push initial counter value

    // Loop until counter reaches zero
    BEGIN
        #1 -        // Decrement counter
        dup         // Duplicate for test condition
    UNTIL          // Loop continues while condition is false (non-zero)
    
    drop           // Clean up the final zero

wait_forever:
     noop
     JMP wait_forever

