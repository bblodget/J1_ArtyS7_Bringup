ORG $0000
JMP 'start

include "core/j1_base_macros.asm"
include "io/terminal_io.asm"

: start
    key        // Read the character
    emit       // Echo it back
    $0A emit  // Send newline (ASCII 0x0A)

: wait_forever
     noop
     JMP 'wait_forever

