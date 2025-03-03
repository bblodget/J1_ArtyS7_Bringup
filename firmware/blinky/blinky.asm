// Tinyfpga-bx Blinky
// Blinks LED on PORTA_01 (pin 14)

ORG #$0000
JMP start

include "core/j1_base_macros.asm"      // Base J1 operations
include "io/terminal_io.asm"

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

: print_on ( -- )
    #$4C emit  // L
    #$45 emit  // E
    #$44 emit  // D
    #$20 emit  // space
    #$4F emit  // O
    #$4E emit  // N
    #$20 emit  // space
    #$0A emit  // Newline
    exit
    ;

: print_off ( -- )
    #$4C emit  // L
    #$45 emit  // E
    #$44 emit  // D
    #$20 emit  // space
    #$4F emit  // O
    #$46 emit  // F
    #$46 emit  // F
    #$0A emit  // Newline
    exit
    ;

delay:
    // Outer loop: 183 iterations
    #100 #0 DO
        #$7FF0 #0 DO
            // Inner loop body (empty for maximum speed)
            noop
        LOOP
    LOOP
    exit

start:
    init_led        // Configure PORTA13 as output

main_loop:
    led_on          // Turn LED on
    print_on        // Print "LED ON" message
    delay           // Wait for delay instead of keypress
    led_off         // Turn LED off
    print_off       // Print "LED OFF" message
    delay           // Wait for delay instead of keypress
    JMP main_loop   // Repeat forever

