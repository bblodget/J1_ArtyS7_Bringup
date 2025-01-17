// Test Status and Control operations
include "core/j1_base_macros.asm"
include "core/j1_extended_macros.asm"

start:
    // Test Status and Control
    depth        // Stack: 0 (current stack depth)
    dint         // Stack: 0 (disable interrupts)
    eint         // Stack: 0 (enable interrupts)

done:
    noop
    JMP done