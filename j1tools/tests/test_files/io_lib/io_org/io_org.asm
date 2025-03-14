ORG $0000
JMP 'start

include "core/j1_base_macros.asm"
include "io/terminal_io.asm"

: start
    CALL 'key        // Read the character
    CALL 'emit       // Echo it back
    $0A CALL 'emit  // Send newline (ASCII 0x0A)

: wait_forever
     noop
     JMP 'wait_forever

