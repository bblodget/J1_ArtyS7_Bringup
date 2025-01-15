# I/O Library Support

## Required ALU Operations

The J1 processor needs these ALU operations to support I/O:

``` python:j1tools/j1tools/assembler/instructionset_16kb_dualport.py
ALU_OPS = {
    # ... existing ops ...
    "io[T]": 0x0D00,  # I/O read operation
    "status": 0x0E00, # Status register
}

STACK_EFFECTS = {
    # ... existing effects ...
    "N->io[T]": 0x0040,  # I/O write operation
    "IORD": 0x0050,      # I/O read modifier
}
```

## Basic I/O Macros

These macros provide the fundamental I/O operations:

``` asm:j1tools/j1tools/assembler/lib/core/j1_base_macros.asm
// I/O operations
macro: io@     ( addr -- val )     io[T][IORD] ;       // Read from I/O
macro: io!     ( val addr -- )     T[N->io[T],d-1] ;   // Write to I/O
macro: tuckio! ( x addr -- )       T[N->io[T],d-1] ;   // Write to I/O preserving value
macro: 2dupio! ( x addr -- x addr) T[N->io[T]] ;       // Write to I/O keeping both values
```

## Grammar Extensions

To support the Forth-style syntax in nucleus-16kb-dualport.fs, add these grammar rules:

``` lark:j1tools/j1tools/assembler/j1.lark
// Cross-compiler directives
HEADER: "header"
HEADER_FOLDABLE: "header-" /[0-9]/ "-foldable"
COLON_NONAME: ":noname"

// Stack effect comments
STACK_COMMENT: /\([^)]*\)/

// Allow Forth-style definitions
forth_def: (HEADER | HEADER_FOLDABLE) IDENT COLON instruction+ SEMICOLON
        | COLON_NONAME instruction+ SEMICOLON
```

## Key I/O Words

The essential I/O words from nucleus-16kb-dualport.fs that need support:

``` forth
header io!      :noname     io!      ;  // Write to I/O port
header io@      :noname     io@      ;  // Read from I/O port
header emit?    : emit? ( -- ? ) pause d# 1 : uartstat h# 2000 io@ overand = ;
header key?     : key?  ( -- ? ) pause d# 2   uartstat ;
```

## Implementation Notes

The main differences from a standard assembler implementation are:

1. Support for Forth-style word definitions with headers
2. Support for stack effect comments
3. Support for immediate values with d# and h# prefixes
4. Support for cross-compiler directives like header and header-n-foldable
5. Support for :noname definitions

These can be implemented as assembly macros that expand to the appropriate J1 instructions, rather than implementing the full cross-compiler functionality.

## Questions

Q: Are we crossing a boundry from an assembler to a compiler?

A: I'd call it an "enhanced assembler with meta-compilation features" - it's more than a pure assembler but not quite a full compiler. This hybrid approach is common in Forth systems where the line between compilation and assembly is traditionally fuzzy.