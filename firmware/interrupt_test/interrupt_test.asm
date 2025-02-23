// Basic Interrupt Test
// Toggles LED on each interrupt

ORG #$0000
JMP main                // Boot vector

ORG #$0002
JMP irq_handler        // Interrupt vector

include "core/j1_base_macros.asm"

// Variables in high memory
ORG #$7F0
: led_state    #0 ;    // Current LED state

// Main program - enables interrupts and loops
: main ( -- )
    #0 led_state !     // Initialize LED state
    eint               // Enable interrupts
    begin              // Main loop
        #1 drop        // No-op to keep CPU busy
    again
    ;

// Interrupt handler - toggles LED
: irq_handler ( -- )
    // Toggle LED state
    led_state @        // Get current state
    #1 xor             // Toggle bit 0
    dup led_state !    // Save new state
    
    // Output to LEDs (assuming LED control at IO address 0)
    #0 io!             // Write to LED control register
    ;
