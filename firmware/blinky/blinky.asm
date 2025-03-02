// Blinks LED on PORTA13

ORG #$0000
JMP start

include "core/j1_base_macros.asm"      // Base J1 operations
include "core/j1_extended_macros.asm"   // HX8K extended operations
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

start:
    init_led        // Configure PORTA13 as output

main_loop:
    led_on          // Turn LED on
    print_on        // Print "LED ON" message
    key drop        // Wait for keypress and discard the key value
    led_off         // Turn LED off
    print_off       // Print "LED OFF" message
    key drop        // Wait for keypress and discard the key value
    JMP main_loop   // Repeat forever
