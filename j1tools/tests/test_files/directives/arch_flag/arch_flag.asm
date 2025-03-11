// Minimal Architecture Flag Test

// Set architecture flags
.arch_flag fetch_type dualport    // Use dual-port memory (ARCH_FETCH_TYPE = 1)
.arch_flag alu_ops original       // Use original ALU operations (ARCH_ALU_OPS = 0)

// Simple test program that does nothing but jump to itself
: start
    #42     // Push 42
    N       // Drop the value (equivalent to 'drop')
    
    // Loop forever
    JMP 'start

