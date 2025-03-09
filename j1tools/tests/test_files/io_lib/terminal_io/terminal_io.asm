ORG $8000
JMP 'start

include "io_ports.asm"

: start
    // Write to IO port
    #$1234 #TX_PORT !      // Write 0x1234 to IO port 0xF000

: wait_forever
     noop
     JMP 'wait_forever

