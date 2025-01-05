# Memory Sections Support

## Overview
This proposal adds support for memory sections to the J1 assembler, allowing better organization of code, data, and constants in memory.

## Motivation
- Separate code from data
- Support different memory types (RAM/ROM)
- Better memory utilization
- Clearer program structure
- Enable more sophisticated linking
- Support for initialization data

## Syntax

### Basic Section Declaration
```forth
SECTION .code
main:               ; Code goes here
    DUP + RET

SECTION .data
counter: #0        ; Initialized data
buffer:  32        ; Reserve 32 words

SECTION .rodata
pi:     #314      ; Constants
msg:    "Hello"   ; String constants

SECTION .bss
stack:   64       ; Uninitialized data (64 words)
```

### Section Attributes
```forth
SECTION .flash READONLY   ; Read-only section
SECTION .ram   RW        ; Read-write section
SECTION .stack NOLOAD    ; Uninitialized section
```

### Memory Configuration
```forth
; Define memory regions
MEMORY flash ORIGIN=#0000 LENGTH=#2000  ; 8K words flash
MEMORY ram   ORIGIN=#2000 LENGTH=#1000  ; 4K words RAM

; Map sections to memory regions
SECTIONS {
    .code   : > flash  ; Code goes to flash
    .rodata : > flash  ; Constants go to flash
    .data   : > ram    ; Variables go to RAM
    .bss    : > ram    ; Uninitialized data in RAM
}
```

## Standard Sections

### .code
- Program instructions
- Default section if none specified
- Typically placed in ROM/flash
- Read-only at runtime

### .data
- Initialized variables
- Copied to RAM at startup
- Read-write at runtime
- Requires initialization data in ROM

### .rodata
- Read-only data (constants)
- String literals
- Lookup tables
- Placed in ROM/flash

### .bss
- Uninitialized data
- Zero-initialized at startup
- Read-write at runtime
- No space in ROM required

## Implementation Details

### Memory Map Generation
```
Memory Map for program.hex:

Section   Start   End     Size   Used   Type
----------------------------------------
.code     0000    1FFF   8K     164    RO
.rodata   2000    23FF   1K     32     RO
.data     4000    43FF   1K     128    RW
.bss      4400    47FF   1K     64     RW

Symbols:
0000  main     (.code)
0010  square   (.code)
2000  pi       (.rodata)
4000  counter  (.data)
4400  stack    (.bss)
```

### Initialization Support
- Data section contents stored after code
- Startup code copies data to RAM
- BSS section zeroed at startup
- Optional initialization bypass flag

### Linker Script Generation
```
# Generated linker configuration
MEMORY {
    flash : ORIGIN = 0x0000, LENGTH = 0x2000
    ram   : ORIGIN = 0x2000, LENGTH = 0x1000
}

SECTIONS {
    .code : {
        *(.code)
    } > flash

    .rodata : {
        *(.rodata)
    } > flash

    .data : {
        _data_start = .;
        *(.data)
        _data_end = .;
    } > ram AT > flash

    .bss : {
        _bss_start = .;
        *(.bss)
        _bss_end = .;
    } > ram
}
```

## Command Line Options

```bash
--section-map              # Generate section map file
--no-section-init         # Skip data initialization
--section-base CODE=addr  # Override section base address
```

## Future Enhancements

1. **Custom Sections**
   - User-defined section types
   - Custom attributes
   - Placement controls

2. **Alignment Controls**
   - Section alignment
   - Symbol alignment
   - Page boundaries

3. **Overlay Support**
   - Memory overlay definitions
   - Runtime loading
   - Shared memory regions