# Simplified Memory Sections (RAM-Only)

## Overview
This implementation provides section support for unified RAM memory systems, typical of FPGA block RAM configurations. All sections reside in RAM with different allocation strategies and attributes.

## Key Differences from Full Spec
- Single memory region (RAM only)
- No physical ROM/flash distinction
- Read-only sections enforced by software checks
- Simplified initialization requirements

## Syntax

### Section Declaration
```forth
SECTION .code       ; Executable code (default)
SECTION .data       ; Initialized variables
SECTION .rodata RO  ; Read-only constants (software-protected)
SECTION .bss NOLOAD ; Uninitialized data (space reservation only)
```

### Memory Configuration
```forth
; Single RAM definition
MEMORY ram ORIGIN=#0000 LENGTH=#8000  ; 32K words

; Section layout within RAM
SECTIONS {
    .code   : > ram  ; Code at base address
    .rodata : > ram  ; Constants after code
    .data   : > ram  ; Initialized data
    .bss    : > ram  ; Uninitialized data at end
}
```

## Section Attributes

| Section  | Attributes         | Content Type         | Initialization |
|----------|--------------------|----------------------|----------------|
| .code    | (default)          | Executable code      | Direct         |
| .data    | RW                 | Initialized variables| Copy required  |
| .rodata  | RO                 | Constants            | Direct         |
| .bss     | NOLOAD             | Zero-initialized     | Runtime clear  |

## Implementation Details

### Memory Layout
```
0x0000 +-------------------+
        | .code             |
        | (executable code) |
        +-------------------+
        | .rodata           |
        | (constants)       |
        +-------------------+
        | .data             |
        | (initialized)     |
        +-------------------+
        | .bss              |
        | (uninitialized)   |
0x7FFF +-------------------+
```

### Key Features
1. **Single Address Space**  
   All sections share the same physical RAM with software-enforced protections

2. **Read-Only Enforcement**  
   Attempts to write to .rodata sections generate assembler errors:
   ```forth
   SECTION .rodata
   table: #1234
   
   SECTION .code
   main:
       #5678 STORE [table]  ; Error: Write to .rodata
   ```

3. **BSS Handling**  
   Reserves space without initialization data:
   ```forth
   SECTION .bss
   buffer: 1024  ; Reserves 1024 words, no hex output
   ```

4. **Data Initialization**  
   Initial values stored directly in code space:
   ```forth
   SECTION .data
   counter: #42  ; Stored as 0x002A in output
   ```

## Example Program
```forth
MEMORY ram ORIGIN=#0000 LENGTH=#1000  ; 4K RAM

SECTIONS {
    .code : > ram
    .data : > ram
}

SECTION .code
main:
    #100 DUP STORE [counter]  ; Valid data write
    HALT

SECTION .data
counter: #0  ; Initialized variable

SECTION .bss
buffer: 32   ; Reserve 32 words
```

## Command Line Options
```bash
--sections            # Enable section support
--no-bss-init         # Skip zero-initialization markers
--ram-size SIZE       # Set RAM size in words (default: 8192)
```

## Future Extensions
1. **Section Alignment**  
   ```forth
   SECTION .data ALIGN=256  ; Align to 256-word boundary
   ```

2. **Custom Sections**  
   ```forth
   SECTION .vectors         ; Interrupt vector table
   ```

3. **Protection Flags**  
   ```forth
   SECTION .critical NOOVERWRITE  ; Critical data section
   ```
