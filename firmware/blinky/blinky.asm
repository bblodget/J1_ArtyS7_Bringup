// Blinks LED on PORTA13

ORG #$0000
JMP start

ORG #$0001
vector:
    // JMP irq        // Interrupt vector
    T[fDINT]        // Disable interrupts
    #$0000                          //  Bit 13 mask (clear bit 13)
    #2                              //  Write back to porta_out
    3OS[N->io[T],d-2]               //  (macro: io!)
    #$49 emit  // I
    #$52 emit  // R
    #$51 emit  // Q
    #$0A emit  // Newline
    T[RET,r-1]                      //  (macro: exit)


include "core/j1_base_macros.asm"      // Base J1 operations
include "io/terminal_io.asm"

// Memory access macro for quickstore
// macro: @       ( addr -- x )           #$4000 or >r ;
// macro: !       ( x addr -- )           3OS[N->[T],d-2] ;

: init_led ( -- )
    // Set outputs
    #$0001          // Set porta_dir[0] to 1 (output)
    #4 io!          // Write to porta_dir
    exit
    ;

: led_on ( -- )
    #$0001          // Bit 13 mask (set bit 13)
    #2 io!          // Write back to porta_out
    exit
    ;

: led_off ( -- )
    #$0000          // Bit 13 mask (clear bit 13)
    #2 io!          // Write back to porta_out
    exit
    ;

: print_irq ( -- )
    #$49 emit  // I
    #$52 emit  // R
    #$51 emit  // Q
    #$0A emit  // Newline
    exit
    ;

start:
    init_led        // Configure PORTA13 as output
    led_on          // Turn LED on initially

    // Put big number in ticks register to force an interrupt soon
    #11 invert #$4000 io!   // Write -10 to ticks register

    eint            // Enable interrupts

main_loop:
    // #$4000 io@ drop // Read ticks register (address 0x4000)
    noop
    JMP main_loop   // Repeat forever

irq: 
    print_irq       // Print "IRQ" to terminal
    led_off         // Turn LED off in interrupt
    exit
