// Terminal I/O Library for J1 Processor
// Implements basic UART communication primitives

include "core/j1_base_macros.asm"

// FIXME: We should not have to jump to start here
// Need to figure out a better way to handle this
// Jump to start
JMP start

// UART Register Addresses
macro: UART_STATUS_REG ( -- addr ) #$2000 ;
macro: UART_DATA_REG   ( -- addr ) #$1000 ;

// Basic utility macros
macro: nop ( -- )
    noop
;

macro: pause ( -- )
    nop
;

// UART Status Check
: uartstat ( mask -- flag )
    UART_STATUS_REG io@ and exit
;

// Check if UART is ready to transmit
: emit? ( -- ? )
    pause
    #1                   // Push transmit ready mask
    UART_STATUS_REG io@  // Get UART status
    over and            // AND with mask
    =                   // Compare result
    exit
;

// Check if UART has received data
: key? ( -- ? )
    pause
    #2                  // Push receive ready mask
    CALL uartstat      // Check UART status
    exit
;

// Send a character to UART
: emit ( c -- )
    swap >r            // Save character to return stack
emit_wait:
    CALL emit?              // Check if ready to transmit
    ZJMP emit_wait     // If not ready, keep waiting
    r>                 // Restore character
    UART_DATA_REG io!  // Send character
    exit
;

// Read a character from UART
: key ( -- c )
    CALL key?              // Check if character available
    ZJMP key         // If no character, keep waiting
    UART_DATA_REG io@ // Read character
    exit
;

// Send two characters to UART
: 2emit ( c2 c1 -- )
    swap >r            // Save second char
    CALL emit               // Send first char
    r> CALL emit           // Send second char
    exit
;
