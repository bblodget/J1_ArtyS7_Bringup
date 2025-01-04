# Parameter Register File Concept for J1 Processor

## Overview
A proposed enhancement to the J1 processor architecture that adds a parameter register file, allowing quick access to frequently used parameters without stack manipulation.

## Key Features
- Single-cycle transfer of multiple stack items to parameter registers
- Direct access to parameters using $1, $2, $3 syntax
- Maintains stack-machine simplicity while adding register-like convenience

## Proposed Instruction
```
8'b011_11010: // >P(n) instruction
    // insn[3:0] contains n (number of parameters to move)
```

## Forth Interface
```
: >P3   $1A03 ; ( n1 n2 n3 -- )  \ Move 3 parameters to parameter file
: >P2   $1A02 ; ( n1 n2 -- )     \ Move 2 parameters
: >P1   $1A01 ; ( n1 -- )        \ Move 1 parameter

\ Example usage
: EXAMPLE ( width height depth -- volume )
    >P3        \ Move all 3 parameters in one cycle
    $1 $2 * $3 *  \ width * height * depth using parameter references
;
```

## Benefits
1. Reduced stack manipulation overhead
2. More readable code for complex operations
3. Efficient access to frequently used values
4. Single-cycle parameter loading

## Parameter Register Scope Management

### The Problem
When a word using parameter registers calls another word that also uses parameter registers, we need a mechanism to preserve and restore parameter context, similar to how the return stack handles return addresses.

### Possible Solutions

1. **Parameter Base Pointer Approach**
- Use a larger parameter space (32 or 64 parameters)
- Parameter Base Pointer (PBP) register points to current word's $1
- Push PBP to parameter return stack when calling new word
- Increment PBP to allocate space for new word's parameters
- Pop and restore PBP on word return
- Parameters always accessed as offset from PBP

2. **BRAM-based Parameter Storage**
- Dedicate a section of dual-port BRAM for parameters (e.g., 0x7E00-0x7EFF)
- Single-cycle access just like register file
- More efficient use of FPGA resources
- Larger parameter space possible
- Takes advantage of existing dual-port memory interface
- Can read parameters while executing other memory operations

### Trade-offs
- BRAM approach saves FPGA fabric resources
- PBP approach provides natural nesting of parameter spaces
- Both solutions provide single-cycle access
- BRAM solution better aligned with J1's existing architecture

## Future Exploration
- Parameter space allocation strategies
- Compiler optimizations for parameter usage
- Integration with existing memory operations
- Optimal parameter space size