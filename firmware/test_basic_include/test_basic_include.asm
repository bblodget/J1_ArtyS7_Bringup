include "words.asm"

start:                         // Note the colon after label
    #42 #10
    dup
    drop
    JMP wait_forever           // Jump to end of program

wait_forever:
    noop            
    JMP wait_forever           // Loop forever
