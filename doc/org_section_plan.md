# ORG and SECTION Implementation Plan

## Overview
This document outlines the implementation strategy for combining ORG directives with section support in a unified RAM memory model. The system will allow precise memory layout control while maintaining section organization benefits.

## Key Requirements
1. Support absolute addressing with ORG
2. Section-based memory organization
3. Collision detection across sections
4. Include file compatibility
5. RAM-only memory model

## Implementation Phases

### Phase 1: Core ORG Support

#### 1. Grammar Extensions (`j1.lark`)
```lark
org_directive: "ORG" value
value: NUMBER | HEX_NUMBER | IDENT

section_decl: "SECTION" section_name attr*
section_name: "." ("code"|"data"|"rodata"|"bss")
attr: "RO" | "NOLOAD"
```

#### 2. Address Tracking
```python
class AddressSpace:
    def __init__(self):
        self.current_org = 0x0000
        self.sections = {
            '.code': {'start': 0x0000, 'current': 0x0000},
            '.data': {'start': None, 'current': None},
            # ... other sections ...
        }
    
    def set_org(self, address):
        if self.current_section == '.code' and address < self.sections['.code']['current']:
            raise OrgError("Cannot ORG backward in .code section")
        self.sections[self.current_section]['current'] = address
```

#### 3. Collision Detection
```python
class CollisionDetector:
    def check(self, start, end):
        for range in self.allocated_ranges:
            if (start >= range['start'] and start <= range['end']) or \
               (end >= range['start'] and end <= range['end']):
                return True
        return False
```

### Phase 2: Section Integration

#### 1. Section-Aware ORG
```forth
SECTION .data
ORG #3000  ; Set .data section address
counter: #0

SECTION .code
ORG #0000  ; Reset .code address
```

#### 2. Attribute Enforcement
```python
def validate_write(section):
    if section == '.rodata':
        raise WriteError("Write to read-only section")
```

#### 3. Memory Region Validation
```python
def validate_region(section, address):
    region = self.memory_map[section['region']]
    if address < region['start'] or address > region['end']:
        raise RegionError(f"Address {address:04x} outside {section['region']}")
```

### Phase 3: Linker and Include Handling

#### 1. Include File Processing
```python
def process_include(file):
    old_sections = copy(current_sections)
    try:
        parse_file(file)
    finally:
        current_sections = old_sections
```

#### 2. Symbol Resolution
```python
class Linker:
    def resolve(self, symbol):
        for module in self.modules:
            if symbol in module.exports:
                return module.base_address + module.symbols[symbol]
        raise UndefinedSymbolError(symbol)
```

#### 3. Memory Map Generation
```python
def generate_map():
    return "\n".join([
        f"{name:8} {start:04X}-{end:04X} {size:4} {used:4} {attrs}",
        # ... section data ...
    ])
```

## Include File Handling Strategy

### Key Principles
1. **Relative Addressing**  
   Included files use section-relative addressing
   ```forth
   ; lib/math.forth
   SECTION .code
   square:         ; Becomes .code+0x0100 in final map
       DUP * RET
   ```

2. **Section Merging**  
   All files' sections are combined:
   ```
   Main file .code: 0x0000-0x01FF
   Library .code:   0x0200-0x02FF
   ```

3. **Late Binding**  
   Final addresses resolved after all includes processed

## Error Checking

| Error Type              | Detection Method                          | Example                  |
|-------------------------|-------------------------------------------|--------------------------|
| Address Collision       | Range tracking during ORG                 | `ORG #1000` after usage  |
| Section Overflow        | Section size vs memory region             | `.data` exceeds RAM      |
| Invalid ORG in Section  | Section attribute checks                  | `ORG` in `.rodata`       |
| Include Scope Bleed     | Symbol table validation                   | Duplicate global symbols |

## Example Usage

### Source Files
`main.forth`:
```forth
MEMORY ram ORIGIN=0 LENGTH=0x1000
INCLUDE "lib.f"

SECTIONS {
    .code : > ram
    .data : > ram
}

SECTION .code
ORG #0000
main:
    CALL lib_func
```

`lib.f`:
```forth
SECTION .code
lib_func:
    RET
```

### Memory Map Output
```
Section   Start   End     Size  Used  Type
-------------------------------------------
.code     0000    0001    2     2     RW
.data     ----    ----    --    0     RW
```

## Future Enhancements

1. **Section Alignment**  
   ```forth
   SECTION .data ALIGN=256  ; Align to 256-byte boundary
   ```

2. **Custom Sections**  
   ```forth
   SECTION .vectors  ; Interrupt vectors
   ORG #0000
   ```

3. **Overlay Support**  
   ```forth
   OVERLAY shared_ram {
       SECTION .temp1 : > ram
       SECTION .temp2 : > ram
   }
   ```

This plan provides a roadmap for implementing ORG and SECTION directives while maintaining compatibility with FPGA RAM constraints and existing toolchain components.

## ORG Within Sections

### Behavior
1. **Section-relative ORG**  
   ORG directives after SECTION set the *absolute address* for subsequent code in that section:
   ```forth
   SECTION .code
   ORG #1000    ; Next instructions start at 0x1000
   main:         ; Address 0x1000
       NOP       ; 0x1001
   ```

2. **Memory Region Constraints**  
   Must stay within section's assigned memory region:
   ```forth
   MEMORY ram ORIGIN=#0000 LENGTH=#2000  ; 8K RAM
   SECTIONS { .code : > ram }
   
   SECTION .code
   ORG #3000  ; Error: Outside RAM region (0000-1FFF)
   ```

3. **Section Restart**  
   ORG can reset address within same section:
   ```forth
   SECTION .code
   label1:       ; 0x0000
   ORG #0000
   label2:       ; Also 0x0000 (collision warning)
   ```

4. **Cross-Section ORG**  
   ORG in one section doesn't affect others:
   ```forth
   SECTION .code
   ORG #1000     ; .code starts at 1000
   SECTION .data
   data: #42     ; .data starts at default (e.g., 2000)
   ```

### Error Cases
1. **Backward ORG**  
   ```forth
   SECTION .code
   org #1000
   org #0800  ; Error: Can't move backward in .code
   ```

2. **RO Section ORG**  
   ```forth
   SECTION .rodata RO
   ORG #1000  ; Error: Read-only section can't set ORG
   ```

3. **BSS Section ORG**  
   ```forth
   SECTION .bss NOLOAD
   ORG #1000  ; Allowed: BSS just reserves space
   ```

### Implementation
```python
def process_org(section, address):
    if section == '.rodata':
        raise OrgError("Can't ORG in read-only section")
        
    if section == '.code' and address < current_code_addr:
        raise OrgError("Can't ORG backward in .code")
        
    if not memory_region.contains(address):
        raise OrgError(f"ORG {address:04x} outside {section} region")
        
    sections[section].current = address
    sections[section].start = address  # Track initial ORG
```

This ensures ORG directives provide precise control while respecting section constraints and memory regions. Would you like to adjust any of these behaviors?

## Reset Vector and Include Ordering

### Default Behavior
1. **Processing Order**  
   Sections are concatenated in source order:
   ```forth
   ; main.forth
   INCLUDE "lib.forth"  ; lib code first
   SECTION .code
   start:          ; Address after lib code
       ...
   ```

2. **Included Files**  
   Appended to current section:
   ```
   Memory Layout:
   0000 : lib_code
   0002 : main_code
   ```

### Critical Address Handling
For code that must start at specific addresses (like reset vectors):

1. **Explicit ORG**  
   ```forth
   SECTION .code
   ORG #0000       ; Force address 0
   reset_vector:
       JMP main    ; Guaranteed at 0000
   
   INCLUDE "lib.forth"  ; Code after 0002
   ```

2. **Include Order Control**  
   ```forth
   SECTION .code
   ORG #0000
       JMP main
   
   ; System includes after reset vector
   INCLUDE "interrupts.forth"
   
   main:            ; After system includes
       ...
   ```

### Error Case Example
**Unsafe Code:**
```forth
; main.forth
INCLUDE "lib.forth"  ; lib code at 0000

SECTION .code
    JMP start       ; Too late! Now at lib_end+1
```

**Safe Solution:**
```forth
; main.forth
SECTION .code
ORG #0000
    JMP start       ; Now at 0000

INCLUDE "lib.forth"  ; lib code starts at 0002
```

### Best Practices
1. **Always ORG Critical Code**  
   Use explicit ORG for:
   - Reset vectors (0000)
   - Interrupt handlers
   - Memory-mapped I/O

2. **Organize Includes**  
   ```forth
   SECTION .code
   ORG #0000
       ; Critical system code
   
   INCLUDE "low_level.forth"
   INCLUDE "high_level.forth"
   
   SECTION .data
       ; Application data
   ```

3. **Section Isolation**  
   ```forth
   SECTION .vectors  ; Special low-address section
   ORG #0000
       JMP main
   
   SECTION .code     ; Normal code section
   main:
       ...
   ```

This addition clarifies how to handle processor startup requirements and avoid subtle ordering bugs in include files.

## Recommended Usage Practices

### When to Use ORG
1. **Hardware-Mandated Addresses**  
   ```forth
   SECTION .vectors
   ORG #0000       ; Reset vector
   reset_jmp: JMP main

   ORG #FF00       ; Memory-mapped I/O
   LED_CONTROL: #0000
   ```

2. **Critical Alignment Needs**  
   ```forth
   SECTION .dma_buffer
   ORG ALIGN(here, 256)  ; 256-byte boundary
   dma_buffer: 256        ; For DMA hardware requirements
   ```

3. **Legacy Code Integration**  
   ```forth
   SECTION .legacy
   ORG #2000       ; Preserve existing binary interface
   legacy_entry:
       CALL original_code
   ```

### When to Prefer SECTION
1. **General Code Organization**  
   ```forth
   SECTION .code
   main:
       ; Automatic address assignment
       CALL initialize
       LOOP run_main

   SECTION .data
   config: #01 #02 #03
   ```

2. **Memory Protection**  
   ```forth
   SECTION .rodata RO
   strings: "Error: ", "Warning: "  ; Protected constants
   ```

3. **Resource Management**  
   ```forth
   SECTION .bss NOLOAD
   stack: 64        ; Uninitialized memory
   heap:  1024      ; Dynamic allocation space
   ```

### Risk Mitigation Strategies

1. **Protected Address Ranges**  
   ```python
   class AddressValidator:
       RESERVED_RANGES = [
           (0x0000, 0x0003),  # Reset vectors
           (0xFF00, 0xFF0F)   # Hardware registers
       ]
       
       def validate_org(self, address):
           for start, end in self.RESERVED_RANGES:
               if start <= address <= end:
                   raise ProtectedAddressError(f"{address:04x} in protected range")
   ```

2. **Section Constraints**  
   ```forth
   SECTIONS {
       .vectors : ORIGIN=#0000 LENGTH=#10 > ram
       .code    : > ram
       .data    : > ram
   }
   ```

3. **Toolchain Checks**  
   - Enable address collision warnings
   - Validate section regions during linking
   - Flag unconstrained ORG usage

### Anti-Patterns to Avoid
```forth
; ❌ Dangerous: Manual address juggling
SECTION .code
ORG #1000
    ; ...
ORG #0800  ; Backward jump in same section

; ✅ Safe: Section-based organization
SECTION .lowcode
ORG #0000
    ; Reset handler

SECTION .highcode
    ; Normal code
```

| Situation              | Recommendation          |
|------------------------|-------------------------|
| Startup code           | ORG #0000 + SECTION     |
| General application    | SECTION only            |
| Shared libraries       | SECTION + relative refs |
| Hardware interaction   | ORG + protected section |

This guidance helps balance flexibility with safety in memory layout management.
