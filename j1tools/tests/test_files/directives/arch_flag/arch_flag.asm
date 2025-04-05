// Architecture Flag Test File
// This file tests the .arch_flag directive

// Set architecture flags
.arch_flag fetch_type FETCH_TYPE_DUALPORT    // Use dual-port memory (ARCH_FETCH_TYPE = 1)
.arch_flag alu_ops ALU_OPS_ORIGINAL         // Use original ALU operations (ARCH_ALU_OPS = 0)

// Simple test program
: main
    42     // Push 42
    N       // Drop the value (equivalent to 'drop')
    
    // Loop forever
    JMP 'main

