ORG $0000
JMP start

include "words.asm"

: start
    // Push two numbers and add them
    #$2A #10             // Push hex 2A (decimal 42) and decimal 10
    CALL add_nums        // Call our addition subroutine
    N[d-1]               // DROP the result
    JMP wait_forever     // Jump to end of program

: wait_forever
     noop
     JMP wait_forever
