ORG #$0000
JMP start

include "platform/j1_16kb_dualport_macros.asm"

: start
    // Initialize loop parameters
    #3              // Push limit (3)
    #0              // Push initial index (0)

    // Save index and limit to R stack
    >r              // Save index (0) to R stack
    >r              // Save limit (5) to R stack

: do_label
    // Loop body - just decrement a counter
    noop           // Do nothing in the loop body for this basic test

    // Loop control
    r>             // Get limit
    r>             // Get index
    1+              // Increment index
    over over      // Duplicate both values for next iteration
    >r             // Save new index back
    >r             // Save limit back
    <              // Compare index < limit
    ZJMP do_label  // Jump if index < limit
    
: wait_forever
    noop
    JMP wait_forever

