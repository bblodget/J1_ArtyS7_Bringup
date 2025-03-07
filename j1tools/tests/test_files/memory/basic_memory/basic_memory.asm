// Test platform for J1 16KB Dual-Port configuration
include "core/j1_base_macros.asm"
include "core/j1_dualport_macros.asm"

// Test program start
ORG #$0000
: start
    // Test basic memory operations
    #1234        // Stack: 1234 (test data)
    #100         // Stack: 1234 100 (test address)
    !            // Stack: empty (write 1234 to addr 100)
    
    #100         // Stack: 100
    @            // Stack: 1234 (read back from addr 100)
    
    // Test multiple memory locations
    #5678        // Stack: 1234 5678
    #102         // Stack: 1234 5678 102
    !            // Stack: 1234 (write 5678 to addr 102)
    
    #102         // Stack: 1234 102
    @            // Stack: 1234 5678 (read back from addr 102)
    
    // Verify first value is still correct
    #100         // Stack: 1234 5678 100
    @            // Stack: 1234 5678 1234 (read back first value)
    
    // Test sequential memory writes
    #101         // Stack: 1234 5678 1234 101
    !            // Stack: 1234 5678 (write 1234 to addr 101)
    #103         // Stack: 1234 5678 103
    !            // Stack: 1234 (write 5678 to addr 103)
    
    // Read back sequential values
    #100         // Stack: 1234 100
    @            // Stack: 1234 1234 (should be 1234)
    #101         // Stack: 1234 1234 101
    @            // Stack: 1234 1234 1234 (should be 1234)
    #102         // Stack: 1234 1234 1234 102
    @            // Stack: 1234 1234 1234 5678 (should be 5678)
    #103         // Stack: 1234 1234 1234 5678 103
    @            // Stack: 1234 1234 1234 5678 5678 (should be 5678)
    JMP done     // Jump to done

ORG #$0020
: done
    noop
    JMP done     // Loop forever
