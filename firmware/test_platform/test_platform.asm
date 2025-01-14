// Test platform for J1 16KB Dual-Port configuration
include "core/j1_base_macros.asm"

// Test program start
start:
    // Test basic stack operations
    #5 #3        // Push 5 and 3 onto stack
    swap         // Stack: 3 5
    over         // Stack: 3 5 3
    nip          // Stack: 3 3
    dup          // Stack: 3 3 3
    drop         // Stack: 3 3
    drop         // Stack: 3

    // Test ALU operations
    #8           // Stack: 3 8
    +            // Stack: 11
    #5           // Stack: 11 5
    -            // Stack: 6
    #3           // Stack: 6 3
    and          // Stack: 2
    #5           // Stack: 2 5
    or           // Stack: 7
    #3           // Stack: 7 3
    xor          // Stack: 4
    invert       // Stack: -5 (0xFFFB)
    
    // Test comparisons
    #10 #5       // Stack: -5 10 5
    u<           // Stack: -5 0 (false: 10 is not < 5)
    drop         // Stack: -5
    #3 #8        // Stack: -5 3 8
    <            // Stack: -5 1 (true: 3 < 8)
    drop         // Stack: -5
    #4 #4        // Stack: -5 4 4
    =            // Stack: -5 1 (true: 4 = 4)
    drop         // Stack: -5

    // Test shifts
    #4           // Stack: -5 4
    2*           // Stack: -5 8
    2/           // Stack: -5 4

    // Test return stack operations
    #42          // Stack: -5 4 42
    >r           // Stack: -5 4, R: 42
    #7           // Stack: -5 4 7
    >r           // Stack: -5 4, R: 42 7
    r@           // Stack: -5 4 7, R: 42 7 (peek at top of return stack)
    r>           // Stack: -5 4 7 7, R: 42
    =            // Stack: -5 4 1 (true: values match)
    r>           // Stack: -5 4 1 42, R: empty
    drop         // Stack: -5 4 1
    drop         // Stack: -5 4

    // Test I/O operations
    #1234        // Stack: -5 4 1234 (test data)
    #42          // Stack: -5 4 1234 42 (test address)
    io!          // Stack: -5 4 (write 1234 to IO addr 42)
    #42          // Stack: -5 4 42
    io@          // Stack: -5 4 1234 (read back from IO addr 42)
    drop         // Stack: -5 4

    // Test Status and Control
    depth        // Stack: -5 4 2 (current stack depth)
    dint         // Stack: -5 4 2 (disable interrupts)
    eint         // Stack: -5 4 2 (enable interrupts)
    
    // Test Basic elided words
    #5 #3        // Stack: -5 4 2 5 3
    2dupand      // Stack: -5 4 2 5 3 1
    drop         // Stack: -5 4 2 5 3
    2dup<        // Stack: -5 4 2 5 3 0
    drop         // Stack: -5 4 2 5 3
    2dup=        // Stack: -5 4 2 5 3 0
    drop         // Stack: -5 4 2 5 3
    2dupor       // Stack: -5 4 2 5 3 7
    drop         // Stack: -5 4 2 5 3
    2dup+        // Stack: -5 4 2 5 3 8
    drop         // Stack: -5 4 2 5 3
    2dup-        // Stack: -5 4 2 5 3 -2
    drop         // Stack: -5 4 2 5 3
    2dupu<       // Stack: -5 4 2 5 3 0
    drop         // Stack: -5 4 2 5 3
    2dupxor      // Stack: -5 4 2 5 3 6
    drop         // Stack: -5 4 2 5 3

    // Test dup>r and over operations
    dup>r        // Stack: -5 4 2 5 3, R: 3
    r>           // Stack: -5 4 2 5 3 3
    drop         // Stack: -5 4 2 5 3
    overand      // Stack: -5 4 2 5 1
    over>        // Stack: -5 4 2 5 0
    over=        // Stack: -5 4 2 5 0
    overor       // Stack: -5 4 2 5 5
    over+        // Stack: -5 4 2 5 10
    overu>       // Stack: -5 4 2 5 0
    overxor      // Stack: -5 4 2 5 0

    // Clean up stack
    drop drop drop drop    // Stack: -5 4

done:
    noop
    JMP done     // Loop forever
