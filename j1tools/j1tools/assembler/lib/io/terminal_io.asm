// Terminal I/O Library for J1 Processor
// Implements basic UART communication primitives

// include "core/j1_base_macros.asm"

// FIXME: We should not have to jump to start here
// Need to figure out a better way to handle this
// Jump to start
// JMP 'start

// UART Register Addresses
macro: UART_STATUS_REG ( -- addr ) #$2000 endmacro
macro: UART_DATA_REG   ( -- addr ) #$1000 endmacro

// Basic utility macros
macro: nop ( -- )
    noop
endmacro

macro: pause ( -- )
    nop
endmacro

// UART Status Check
: uartstat ( mask -- flag )
    UART_STATUS_REG io@ overand = 
;

// Check if UART is ready to transmit
: emit? ( -- ? )
    pause
    #1                   // Push transmit ready mask
    UART_STATUS_REG io@  // Get UART status
    overand              // Duplicate status
    =                   // Compare result
;

// Check if UART has received data
: key? ( -- ? )
    pause
    #2                  // Push receive ready mask
    uartstat      // Check UART status
;

// Send a character to UART
: emit ( c -- )
    emit?              // Check if ready to transmit
    ZJMP 'emit     // If not ready, keep waiting
    UART_DATA_REG io!  // Send character
;

// Read a character from UART
: key ( -- c )
    key?              // Check if character available
    ZJMP 'key         // If no character, keep waiting
    UART_DATA_REG io@ // Read character
;

// Send two characters to UART
: 2emit ( c2 c1 -- )
    swap >r            // Save second char
    emit               // Send first char
    r> emit           // Send second char
;
