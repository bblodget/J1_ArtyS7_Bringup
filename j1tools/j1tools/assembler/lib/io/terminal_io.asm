// Terminal I/O Library for J1 Processor
// Implements basic UART communication primitives

// Memory-mapped UART registers
macro: UART_STATUS_REG ( -- addr ) #$2000 ;
macro: UART_DATA_REG   ( -- addr ) #$1000 ;

// Basic Operations
macro: nop ( -- )
    noop        // Use standard noop macro
;

macro: pause ( -- )
    nop         // Currently just a noop
;

// UART Status Operations
: uartstat ( mask -- flag )
    UART_STATUS_REG    // Expands to #$2000
    io@
    and
    exit
;

// Transmit Operations
: emit? ( -- ? )
    pause
    #1                   // Push transmit ready mask
    UART_STATUS_REG     // Push status register address
    io@                 // Read status
    over                // Duplicate mask for comparison
    and                 // Mask the status bits
    =                   // Compare with mask
    exit
;

: emit ( c -- )
begin:
    emit?              // Check if ready to transmit
    ZJMP begin        // Loop until ready
    UART_DATA_REG    // Push data register address
    io!               // Write character
    exit
;

: 2emit ( c2 c1 -- )
    emit               // Output first character
    emit               // Output second character
    exit
;

// Receive Operations
: key? ( -- ? )
    pause
    #2 uartstat         // Use uartstat macro with receive mask
    exit
;

: key ( -- c )
begin:
    key?                // Check for input
    ZJMP begin         // Loop until ready
    UART_DATA_REG     // Push data register address
    io@                // Read character
    exit
;
