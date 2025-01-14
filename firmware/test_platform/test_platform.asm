// Test platform for J1 16KB Dual-Port configuration
//include "platform/j1_16kb_dualport_macros.asm"
include "core/j1_base_macros.asm"

// Test program start
start:
    // Test basic stack operations
    #5 #3        // Push 5 and 3 onto stack
    swap         // Stack: 3 5
    +            // Stack: 8
    #10          // Push 10 onto stack
    u<           //Stack: -1 (true) 8 u< 10
    drop         // Stack: 
    //+            // Stack: 8
    //2dup         // Stack: 5 3 5 3
    // swap         // Stack: 5 8 3
    //drop         // Stack: 5 8

    JMP done

    // Test ALU operations
    //2dup*        // Stack: 5 8 40
    //2/           // Stack: 5 8 20
    //2*           // Stack: 5 8 40

    // Test memory operations
    //#42 #100 !   // Store 42 at address 100
    //#100 @       // Read from address 100
    
    // Test extended operations
    //#3 #1 lshift // Shift 3 left by 1 -> 6
    //#8 #2 rshift // Shift 8 right by 2 -> 2

    // Test return stack
    //>r           // Move value to return stack
    //r@           // Copy from return stack
    //r>           // Restore from return stack

    // Test increment/decrement
    //#10
    //dup1+        // Stack: 10 11
    //1-           // Stack: 10 10

    // Test optimized memory operations
    //#200 dup@    // Read and keep address
    //tuck!        // Store and keep value

done:
    //noop
    JMP done     // Loop forever
