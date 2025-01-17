# Terminal I/O Library for J1 Assembler

This library implements basic terminal input/output functionality for the J1 processor.

## Core Words

### Stack Effect Notation
- `( -- )` means no stack inputs or outputs
- `( -- ? )` means outputs a boolean flag
- `( c -- )` means consumes a character
- `( -- c )` means produces a character
- `( c2 c1 -- )` means consumes two characters

### Constants
```j1asm
// Define constants as macros
macro: UART_STATUS_REG ( -- addr ) #$2000 ;
macro: UART_DATA_REG   ( -- addr ) #$1000 ;
```

### Core Words

#### NOP - No Operation
```j1asm
: nop ( -- )
    noop        // Use standard noop macro
    exit
;
```

#### PAUSE - Minimal Delay
```j1asm
: pause ( -- )
    nop         // Currently just a noop
    exit
;
```

#### UARTSTAT - Check UART Status
```j1asm
: uartstat ( mask -- flag )
    UART_STATUS_REG    // Expands to #$2000
    io@
    and
    exit
;
```

#### EMIT? - Check if UART Ready for Output
```j1asm
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
```

#### KEY? - Check for Input Ready
```j1asm
: key? ( -- ? )
    pause
    #2 uartstat         // Use uartstat macro with receive mask
    exit
;
```

#### KEY - Wait for and Read Input
```j1asm
: key ( -- c )
begin:
    key?                // Check for input
    ZJMP begin         // Loop until ready
    UART_DATA_REG     // Push data register address
    io@                // Read character
    exit
;
```

#### EMIT - Output Character
```j1asm
: emit ( c -- )
begin:
    emit?              // Check if ready to transmit
    ZJMP begin        // Loop until ready
    UART_DATA_REG    // Push data register address
    io!               // Write character
    exit
;
```

#### 2EMIT - Output Two Characters
```j1asm
: 2emit ( c2 c1 -- )
    emit               // Output first character
    emit               // Output second character
    exit
;
```

## Usage Example
```j1asm
// Print "Hi!"
: main
    #'H' emit
    #'i' emit
    #'!' emit
    halt
;
```

## Implementation Notes

1. All words use standard library macros from j1_base_macros.asm
2. UART registers are memory-mapped:
   - Status register at 0x2000
   - Data register at 0x1000
3. Status register bits:
   - Bit 1: Transmit ready
   - Bit 2: Receive ready
4. The PAUSE word can be enhanced later for actual timing control

## Required Grammar Changes

To support Forth-style word definitions and literals, the following changes to j1.lark are needed:

```lark
// Add colon definition syntax to label rule
label: COLON IDENT instruction+ SEMICOLON  // Forth-style ": word ... ;"
     | IDENT COLON                         // Traditional "word:"

// Add tokens for Forth-style definitions
COLON: ":"
SEMICOLON: ";"

// Add literal syntax support
DECIMAL: "#" /[0-9]+/                      // Decimal literals like #42
HEX: "#$" /[0-9A-Fa-f]+/                  // Hex literals like #$2A
CHAR: "[char]" /[^\s]/                     // Character literals like [char] H

// Add stack effect comment support
STACK_COMMENT: /\([^)]*\)/     // Matches "( -- )", "( n -- )", etc.
%ignore STACK_COMMENT          // Optional - ignore in parse tree

// Update literal rule
literal: DECIMAL
       | HEX
       | CHAR

// Update statement rule to handle new label format
statement: label 
        | instruction 
        | macro_def 
        | include_stmt
```

Key grammar changes:
1. Added Forth-style colon definitions
2. Made stack effect comments optional documentation
3. Preserved backward compatibility with label: syntax
4. Added support for decimal (#), hex (#$), and character ([char]) literals
5. Integrated with existing macro and include support

Example usage:
```j1asm
: main
    [char] H emit    // Using ice-mecrisp style character literal
    [char] i emit
    [char] ! emit
    halt
;