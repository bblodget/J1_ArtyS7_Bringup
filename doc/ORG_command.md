# ORG Directive Specification

## Overview
The `ORG` directive sets the current assembly address, enabling precise control over memory layout in RAM-based systems. This is particularly useful for:

- Memory-mapped I/O access
- Interrupt vector tables
- Specialized memory regions
- Code relocation

## Syntax
```forth
ORG <address>
```
- **address**: Absolute 16-bit address (hex: `#$xxxx`, decimal: `#1234`, symbol: `label`)

## Key Features

### 1. Address Control
```forth
ORG #2000       ; Set assembly address to 0x2000
main:
    NOP         ; Assembled at 0x2000
    RET         ; Assembled at 0x2001
```

### 2. Multiple ORG Directives
```forth
    ORG #0000
reset_vector:
    JMP main    ; @ 0x0000

    ORG #2000
main:           ; @ 0x2000
    NOP
```

### 3. Collision Detection
```forth
ORG #1000
data: #1234     ; Occupies 0x1000-0x1001

ORG #1000       ; Error: Address collision at 1000
conflict: #5678
```

### 4. Listing Support
```
ADDRESS  CODE  SOURCE
0000     6000  ORG #0000
0000     6000  reset_vec: JMP main
...
2000     8000  ORG #2000
2000     8000  main: NOP
```

## Use Cases

### 1. Interrupt Vectors
```forth
ORG #0000
reset_vector:
    JMP main        ; @ 0x0000
    NOP             ; @ 0x0001

ORG #0008
timer_int:
    JMP isr_timer   ; @ 0x0008
```

### 2. Memory-Mapped I/O
```forth
ORG #1000
uart_status:  #0     ; Status register @ 0x1000
uart_data:   #0     ; Data register @ 0x1001
```

### 3. Code Relocation
```forth
; Bootloader at start of RAM
ORG #0000
bootloader:
    ...             ; @ 0x0000-0x00FF

; Main application at 0x0100
ORG #0100
main:
    ...             ; @ 0x0100+
```

## Implementation Details

### 1. Grammar Extension
```lark
org_directive: "ORG" value
value: NUMBER | HEX_NUMBER | IDENT
```

### 2. Assembler Behavior
- Sets internal address counter
- Validates address range (0x0000-0xFFFF)
- Tracks used address ranges
- Generates absolute addresses in output

### 3. Collision Detection
```python
class AddressTracker:
    def __init__(self):
        self.used_ranges = []
    
    def check_org(self, new_addr, size):
        for start, end in self.used_ranges:
            if new_addr >= start and new_addr < end:
                raise OrgCollisionError(f"Address {new_addr:04x} in used range {start:04x}-{end:04x}")
        self.used_ranges.append((new_addr, new_addr + size))
```

## Error Handling

| Error Case               | Example               | Error Message                          |
|--------------------------|-----------------------|----------------------------------------|
| Address overflow         | `ORG #FFFF` + 2 bytes | "Address overflow at FFFF"             |
| Negative address         | `ORG #-1`             | "Invalid negative address: -1"        |
| Symbolic address missing | `ORG undefined_label` | "Undefined symbol: undefined_label"    |
| Range collision          | Overlapping ORG       | "Address collision at 1000-1001"      |

## Future Enhancements

1. **Alignment Directives**
```forth
ALIGN 256      ; Align next ORG to 256-byte boundary
```

2. **Linking Support**
```forth
ORG extern_buffer  ; Set address to external symbol
```

3. **Section-Relative ORG**
```forth
SECTION .data
    ORG #100     ; Offset within section
```

4. **ORG Ranges**
```forth
ORG #1000-#1FFF  ; Allocate within specific range
```

This specification provides precise memory layout control while maintaining compatibility with FPGA RAM constraints. Would you like to refine any particular aspect or focus on implementation details next?
