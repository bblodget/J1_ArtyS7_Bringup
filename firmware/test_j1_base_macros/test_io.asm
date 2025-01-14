// Test I/O operations
include "core/j1_base_macros.asm"

start:
    // Test I/O operations
    #1234        // Stack: 1234 (test data)
    #42          // Stack: 1234 42 (test address)
    io!          // Stack: empty (write 1234 to IO addr 42)
    #42          // Stack: 42
    io@          // Stack: 1234 (read back from IO addr 42)

done:
    noop
    JMP done