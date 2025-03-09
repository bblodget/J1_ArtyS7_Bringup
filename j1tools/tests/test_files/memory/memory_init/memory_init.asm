// Test direct memory initialization with comma syntax
include "core/j1_base_macros.asm"
include "core/j1_dualport_macros.asm"

ORG $0000

// Initialize memory with decimal values
10,
20,
30,

// Initialize memory with hex values
$A1,
$B2,
$C3,

// Some code using the initialized values
// The values are at addresses 0, 1, 2, 3, 4, 5
#$0000 @     // Load value at address 0 (10)
#$0001 @     // Load value at address 1 (20)
+           // Add them (should be 30)

: wait_forever
    noop
    wait_forever