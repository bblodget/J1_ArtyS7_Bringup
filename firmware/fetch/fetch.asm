// Fetch test program

ORG #$0000
JMP start

// word address 2, byte address 4
macro: IRQ_COUNT0 ( -- ) #$0004 ;
macro: IRQ_COUNT1 ( -- ) #$0006 ;


ORG #$0008
include "core/j1_base_macros.asm"      // Base J1 operations
include "io/terminal_io.asm"

// Memory access macro for quickstore
macro: @       ( addr -- x )           #$4000 or >r exit ;
macro: !       ( x addr -- )           3OS[N->[T],d-2] ;

start:
    // wait for keypress
    key drop
    
    // Save 8 into IRQ_COUNT0
    #8 IRQ_COUNT0 !

    #$6c >r  // Push return address

    IRQ_COUNT0     // Address to fetch from
    #$4000 or  // Set bit 14
    >r         // Push fetch address
    // Print something before exit
    #$41 emit  // 'A' - to show we got here
    exit       // Trigger fetch
    
return_here:    // this is byte address 6a
    #$42 emit  // 'B' - to show fetch worked
    // Print value of IRQ_COUNT0
    #$30 +         // n + 30, Convert to ASCII by adding '0' (0x30)
    emit
    
main_loop:
    noop
    JMP main_loop   // Repeat forever

