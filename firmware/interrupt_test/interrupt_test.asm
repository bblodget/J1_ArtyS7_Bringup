// Basic Interrupt Test
// Toggles LED on each interrupt

ORG #$0000
JMP start                // Boot vector

ORG #$0001             // word addresss 1, but byte address 2
JMP irq_handler        // Interrupt vector


// word address 2, byte address 4
macro: IRQ_COUNT0 ( -- ) #$0004 ;
macro: IRQ_COUNT1 ( -- ) #$0006 ;

ORG #$0008             // Give some space for the variables above
include "core/j1_base_macros.asm"
include "io/terminal_io.asm"

// ######   IO PORTS   ######################################
//
//        bit READ (into FPGA)    WRITE
//
//    0001  0   porta_in
//    0002  1   porta_out       porta_out
//    0004  2   porta_dir       porta_dir
//    0008  3   spi             spi
//
//    1000  12  UART RX         UART TX
//    2000  13  spi,uart
//    4000  14  ticks           clear ticks
//    8000  15  cycles
//
macro: PORTA_DIR ( -- ) #$0004 ;
macro: PORTA_OUT ( -- ) #$0002 ;
macro: PORTA_IN ( -- ) #$0001 ;

// Memory access macro for quickstore
macro: !       ( x addr -- )           3OS[N->[T],d-2] ;

@:       
    // ( addr -- x )
    #$4000 or >r exit

led_init:
    // Set outputs
    #$0001          // Set porta_dir[0] to 1 (output)
    PORTA_DIR io!          // Write to porta_dir
    exit

led_on:
    #$0001          // Bit 13 mask (set bit 13)
    PORTA_OUT io!          // Write back to porta_out
    exit

led_off:
    #$0000          // Bit 13 mask (clear bit 13)
    PORTA_OUT io!          // Write back to porta_out
    exit

led_toggle: 
    PORTA_OUT io@      // Get current LED state
    #1 xor              // Toggle the LED
    PORTA_OUT io!      // Write back to PORTA
    exit

print_toggle:
    #$54 emit  // T
    #$4F emit  // O
    #$0A emit  // Newline
    exit

print_start:
    #$53 emit  // S
    #$74 emit  // t
    #$61 emit  // a
    #$72 emit  // r
    #$74 emit  // t
    #$0A emit  // Newline
    exit


// Main program - enables interrupts and loops
start:
    // Wait for keypress
    key drop
    print_start
    led_init
    led_on

    // Initialize IRQ_COUNT0
init:
    #0 IRQ_COUNT0 !
    #0 IRQ_COUNT1 !
    eint               // Enable interrupts
main_loop:
    IRQ_COUNT1 @ #2 > IF
        dint    // disable interrupts
        led_toggle
        print_toggle
        JMP init
    THEN
    JMP main_loop


// Interrupt handler - toggles LED
irq_handler:
    dint                    // Disable interrupts
    
    // Emit a character to confirm we're in the handler
    #$41 emit              // 'A' - to show we entered the handler
    
    // Increment IRQ_COUNT0
    IRQ_COUNT0 @           // Fetch current count
    #1 +                   // Increment
    dup                    // Duplicate for comparison
    IRQ_COUNT0 !           // Store back
    
    // Check if we've reached the threshold
    #20 >               // Compare with threshold
    IF
        #$42 emit          // 'B' - to show we entered the IF block
        IRQ_COUNT1 @       // Fetch IRQ_COUNT1
        #1 +               // Increment
        IRQ_COUNT1 !       // Store back
        #0 IRQ_COUNT0 !    // Reset IRQ_COUNT0
    THEN
    
    #$43 emit              // 'C' - to show we're exiting the handler
    exit
