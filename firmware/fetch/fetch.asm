// Fetch test program

ORG $0000
JMP start

// word address 2, byte address 4
macro: IRQ_COUNT0 ( -- ) #$0004 endmacro
macro: IRQ_COUNT1 ( -- ) #$0006 endmacro


ORG $0008
include "core/j1_base_macros.asm"      // Base J1 operations
include "io/terminal_io.asm"

// Memory access macro for quickstore
macro: !       ( x addr -- )           3OS[N->[T],d-2] endmacro

: @ ( addr -- x )
    #$4000 or >r ;

: start
    // wait for keypress
    key drop
    
    // Save 8 into IRQ_COUNT0
    #8 IRQ_COUNT0 !

    #$43 emit  // 'C' - to show we got here
    IRQ_COUNT0 @     // Address to fetch from

: return_here    // this is byte address 6a
    #$44 emit  // 'D' - to show fetch worked
    // Print value of IRQ_COUNT0
    #$30 +         // n + 30, Convert to ASCII by adding '0' (0x30)
    emit
    
: main_loop
    noop
    JMP main_loop   // Repeat forever

