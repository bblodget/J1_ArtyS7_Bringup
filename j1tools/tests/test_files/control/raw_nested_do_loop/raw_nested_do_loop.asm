ORG $0000
JMP 'start

include "platform/j1_16kb_dualport_macros.asm"

: start
    // Outer loop (k): 0 to 2
    3              // Push limit (3)
    0              // Push initial index (0)
    >r              // Save index (0) to R stack
    >r              // Save limit (3) to R stack

: k_loop
    // Middle loop (j): 0 to 1
    2              // Push limit (2)
    0              // Push initial index (0)
    >r              // Save index (0) to R stack
    >r              // Save limit (2) to R stack

: j_loop
    // Inner loop (i): 0 to 3
    4              // Push limit (4)
    0              // Push initial index (0)
    >r              // Save index (0) to R stack
    >r              // Save limit (4) to R stack

: i_loop
    // Access k (outer loop index)
    r>              // Get i limit
    r>              // Get i index
    r>              // Get j limit
    r>              // Get j index
    r>              // Get k limit
    r>              // Get k index
    dup             // Duplicate k index for use
    >r              // Save k index back
    swap            // Bring k limit to top
    >r              // Save k limit back
    swap            // Bring j index to top
    >r              // Save j index back
    swap            // Bring j limit to top
    >r              // Save j limit back
    swap            // Bring i index to top
    >r              // Save i index back
    swap            // Bring i limit to top
    >r              // Save i limit back
    drop            // Discard k value

    // Access j (middle loop index)
    r>              // Get i limit
    r>              // Get i index
    r>              // Get j limit
    r>              // Get j index
    dup             // Duplicate j index for use
    >r              // Save j index back
    swap            // Bring j limit to top
    >r              // Save j limit back
    swap            // Bring i index to top
    >r              // Save i index back
    swap            // Bring i limit to top
    >r              // Save i limit back
    drop            // Discard j value

    // Access i (inner loop index)
    r>              // Get i limit
    r>              // Get i index
    dup             // Duplicate i index for use
    >r              // Save i index back
    swap            // Bring i limit to top
    >r              // Save i limit back
    drop            // Discard i value

    // Inner loop control
    r>              // Get limit
    r>              // Get index
    1+              // Increment index
    over over       // Duplicate both values for next iteration
    >r              // Save new index back
    >r              // Save limit back
    <               // Compare index < limit
    ZJMP 'i_loop     // Jump if index < limit
    rdrop           // Clean up inner loop limit
    rdrop           // Clean up inner loop index

    // Middle loop control
    r>              // Get limit
    r>              // Get index
    1+              // Increment index
    over over       // Duplicate both values for next iteration
    >r              // Save new index back
    >r              // Save limit back
    <               // Compare index < limit
    ZJMP 'j_loop     // Jump if index < limit
    rdrop           // Clean up middle loop limit
    rdrop           // Clean up middle loop index

    // Outer loop control
    r>              // Get limit
    r>              // Get index
    1+              // Increment index
    over over       // Duplicate both values for next iteration
    >r              // Save new index back
    >r              // Save limit back
    <               // Compare index < limit
    ZJMP 'k_loop     // Jump if index < limit
    rdrop           // Clean up outer loop limit
    rdrop           // Clean up outer loop index

: wait_forever
    noop
    JMP 'wait_forever

