// prints 
// Hello 0 
// Hello 1
// ..
// Hello 9

ORG $0000
JMP 'start

include "core/j1_base_macros.asm"      // Base J1 operations
include "io/terminal_io.asm"

: print_hello ( n -- )
    
    // Print "Hello "
    $48 emit  // H
    $65 emit  // e
    $6C emit  // l
    $6C emit  // l
    $6F emit  // o
    $20 emit  // space
    
    // Print number
    $30 +         // n + 30, Convert to ASCII by adding '0' (0x30)
    emit      // Print the number
    
    // Print newline
    $0A emit  // Newline
    ;   // ; by itself generates RET not T[RET,r-1] FIXME

: start
    // Wait for keypress
    key drop        // FIXME: we need to implement key? in simulator

    // Initialize loop parameters
    9             // Push limit (9)
    0             // Push initial index (0)

    // Loop from 0 to 9 inclusive
    DO
        i print_hello
    LOOP

    start

: wait_forever
    noop
    JMP 'wait_forever
