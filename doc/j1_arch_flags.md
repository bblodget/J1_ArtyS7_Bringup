# J1 Architecture Flags

This document describes the configuration flags for the J1 architecture variants supported by the assembler and the associated directive system.

## Architecture Constants

The J1 assembler defines standard constants for configuration options:

```verilog
// Memory Configuration Options
.define FETCH_TYPE_QUICKSTORE 0  // Single-port with write-before-read pattern
.define FETCH_TYPE_DUALPORT   1  // True dual-port memory access

// ALU Operation Set Options  
.define ALU_OPS_ORIGINAL  0      // Original J1 ALU operations only
.define ALU_OPS_EXTENDED  1      // Extended ALU operations including HX8K additions
```

## Architecture Configuration

Architecture flags are set using the `.arch_flag` directive, which requires named constants for both the flag name and value:

```verilog
// Configure memory access pattern
.arch_flag ARCH_FETCH_TYPE FETCH_TYPE_DUALPORT

// Configure ALU operation set
.arch_flag ARCH_ALU_OPS ALU_OPS_EXTENDED
```

Note: The `.arch_flag` directive requires named constants for both the flag name and value. Raw numbers are not allowed. This ensures type safety and makes the code more self-documenting.

Each `.arch_flag` directive automatically defines a corresponding constant that can be queried in conditional code:

```verilog
ARCH_FETCH_TYPE  // 0 = FETCH_TYPE_QUICKSTORE, 1 = FETCH_TYPE_DUALPORT
ARCH_ALU_OPS     // 0 = ALU_OPS_ORIGINAL, 1 = ALU_OPS_EXTENDED
```

### Default Values

The assembler provides default values for architecture flags if they are not explicitly set:

```verilog
ARCH_FETCH_TYPE = 0  // Defaults to FETCH_TYPE_QUICKSTORE
ARCH_ALU_OPS    = 0  // Defaults to ALU_OPS_ORIGINAL
```

These defaults ensure that:
1. The assembler always has valid values for architecture flags
2. Code will work even if architecture flags are not explicitly set
3. The most conservative (widely compatible) options are used by default

## Memory Configuration Details

The J1's memory access pattern is determined by the type of Block RAM (BRAM) available in your target FPGA. Different FPGA families support different BRAM configurations, which affects instruction fetching and data access capabilities.

### BRAM Types and Their Characteristics

#### True Dual-Port BRAM (`FETCH_TYPE_DUALPORT`)
- Supports simultaneous read and write operations
- Can perform instruction fetch and data access in the same cycle
- Available in Xilinx/AMD FPGA families
- Example usage:
```verilog
.arch_flag ARCH_FETCH_TYPE FETCH_TYPE_DUALPORT
```

#### Pseudo Dual-Port BRAM (`FETCH_TYPE_QUICKSTORE`)
- Can perform one read and one write simultaneously
- Cannot perform two reads or two writes in the same cycle
- Since instruction fetch requires a read every cycle:
  - Data writes can complete in 1 cycle ("quickstore")
  - Data reads require multiple cycles (must interleave with instruction fetch)
- Supported in Lattice iCE40 family of FPGAs
- Example usage:
```verilog
.arch_flag ARCH_FETCH_TYPE FETCH_TYPE_QUICKSTORE
```

#### Single-Port BRAM
- Can only perform one operation (read OR write) per cycle
- Requires interleaving of instruction fetch with data access
- Most restrictive in terms of memory access patterns
- Note: Currently not directly supported in arch flags

### Implementation Considerations

1. **Instruction Fetch Priority**
   - The J1 must fetch an instruction every cycle
   - Memory access patterns must work around this requirement

2. **Performance Impact**
   - DUALPORT: Single-cycle data operations possible
   - QUICKSTORE: Writes are fast, reads take multiple cycles
   - Single-port: All data operations take multiple cycles

3. **FPGA Family Selection**
   - Xilinx/AMD FPGAs: Can use DUALPORT mode
   - Lattice iCE40: Use QUICKSTORE mode
   - Check your specific FPGA family's BRAM capabilities

### Best Practices

1. **Memory Access Pattern**
   ```verilog
   // For QUICKSTORE, reads need to account for multi-cycle latency
   .if ARCH_FETCH_TYPE == FETCH_TYPE_QUICKSTORE
       // Add appropriate cycle handling for reads
   .endif
   ```

2. **Performance Optimization**
   - Group reads together when possible
   - Use DUALPORT when available in your FPGA
   - Consider using registers for frequently accessed data

3. **Resource Planning**
   - Choose appropriate memory configuration based on your FPGA family
   - Consider using different memory regions for different access patterns

## ALU Operation Sets

### Supported Variants

The J1 assembler currently supports two ALU operation sets:

### ALU_OPS_ORIGINAL (Base Operations)
Basic J1 ALU operations (0x0000-0x0F00):
```verilog
T      0x0000   // Copy top of stack
N      0x0100   // Copy next on stack
T+N    0x0200   // Add top two items
T&N    0x0300   // Bitwise AND
T|N    0x0400   // Bitwise OR
T^N    0x0500   // Bitwise XOR
~T     0x0600   // Bitwise NOT
N==T   0x0700   // Equal comparison
N<T    0x0800   // Signed less than
T2/    0x0900   // Shift right by 1
T2*    0x0A00   // Shift left by 1
rT     0x0B00   // Copy from return stack
N-T    0x0C00   // Subtract
io[T]  0x0D00   // I/O read
status 0x0E00   // Get data stack depth
Nu<T   0x0F00   // Unsigned less than
```

These base operations are used to create fundamental macros like:
```verilog
// Stack operations
dup     ( a -- a a )        T[T->N,d+1]     // Duplicate top
drop    ( a -- )            N[d-1]          // Discard top
swap    ( a b -- b a )      N[T->N]         // Exchange top two
over    ( a b -- a b a )    N[T->N,d+1]     // Copy second item

// Arithmetic/Logic
+       ( a b -- c )        T+N[d-1]        // Add
-       ( a b -- c )        N-T[d-1]        // Subtract
and     ( a b -- c )        T&N[d-1]        // Bitwise AND
or      ( a b -- c )        T|N[d-1]        // Bitwise OR
xor     ( a b -- c )        T^N[d-1]        // Bitwise XOR
invert  ( a -- ~a )         ~T              // Bitwise NOT
```

### ALU_OPS_EXTENDED (HX8K Extensions)
Additional operations (0x1000-0x1900):
```verilog
NlshiftT   0x1000   // N left shift by T bits
NrshiftT   0x1100   // N right shift by T bits (logical)
NarshiftT  0x1200   // N right shift by T bits (arithmetic)
rstatus    0x1300   // Get return stack depth
L-UM*      0x1400   // Unsigned multiply (low word)
H-UM*      0x1500   // Unsigned multiply (high word)
T+1        0x1600   // Increment top of stack
T-1        0x1700   // Decrement top of stack
3OS        0x1800   // Third item on stack
mem[T]     0x1900   // Direct memory access
```

These extended operations enable higher-level macros:
```verilog
// Extended shift operations
lshift    ( x n -- x<<n )    NlshiftT[d-1]
rshift    ( x n -- x>>n )    NrshiftT[d-1]
arshift   ( x n -- x>>n )    NarshiftT[d-1]

// Extended arithmetic
um*low    ( u1 u2 -- ul )    L-UM*[d-1]     // Multiply low
um*high   ( u1 u2 -- uh )    H-UM*[d-1]     // Multiply high
1+        ( n -- n+1 )       T+1            // Increment
1-        ( n -- n-1 )       T-1            // Decrement

// Stack inspection
rdepth    ( -- n )           rstatus[T->N,d+1]
```

### Other J1 Variants (Not Currently Supported)

While our implementation focuses on the original J1 and HX8K extensions, other J1 variants exist in the ecosystem:

#### Hana 1 Extensions
The Hana 1 adds SPI bus control operations:
- `spi@` - Read a 16-bit value from SPI
- `spi!` - Write a 16-bit value to SPI
- `cs-`  - Turn off chip select for the FLASH

Note: These extensions are not currently supported in our implementation but are documented here for completeness.

### Stack Effect Modifiers
Operations can be combined with stack effect modifiers:
```verilog
T->N     0x0010   // Copy T to N
T->R     0x0020   // Copy T to return stack
N->[T]   0x0030   // Store to memory
N->io[T] 0x0040   // Write to I/O
IORD     0x0050   // I/O read
fDINT    0x0060   // Disable interrupts
fEINT    0x0070   // Enable interrupts
RET      0x0080   // Return from subroutine
```

Stack delta modifiers:
```verilog
// Data stack (dd)
d+0   0x0000   // No change
d+1   0x0001   // Push
d-2   0x0002   // Pop two
d-1   0x0003   // Pop one

// Return stack (rr)
r+0   0x0000   // No change
r+1   0x0004   // Push
r-2   0x0008   // Pop two
r-1   0x000C   // Pop one
```

## Conditional Assembly

The assembler supports conditional assembly based on architecture flags:

```verilog
.if ARCH_FETCH_TYPE == FETCH_TYPE_DUALPORT
    // Dual-port specific code
.else
    // Quickstore specific code
.endif

.if ARCH_ALU_OPS == ALU_OPS_EXTENDED
    // Code using extended ALU operations
.endif
```

Additional conditional directives:

```verilog
.ifdef ARCH_FETCH_TYPE
    // Code included if ARCH_FETCH_TYPE is defined
.endif

.ifndef CUSTOM_FEATURE
    // Code included if CUSTOM_FEATURE is not defined
.endif
```

## Best Practices

1. Set architecture flags at the start of your assembly file
2. Use the predefined constants rather than magic numbers
3. Always check architecture requirements in conditional code
4. Document any architecture-specific requirements in your code

Example:
```verilog
// Declare architecture requirements
.arch_flag ARCH_FETCH_TYPE FETCH_TYPE_DUALPORT
.arch_flag ARCH_ALU_OPS ALU_OPS_EXTENDED

// Document requirements
// This code requires dual-port memory and extended ALU operations
// for optimal performance

// Use architecture-specific features safely
.if ARCH_ALU_OPS == ALU_OPS_EXTENDED
    // Use extended ALU operations
    NlshiftT    // Shift left
    H-UM*       // High multiply
.else
    // Fallback implementation for basic ALU
    2*          // Shift left
    um*         // Basic multiply
.endif
```

## Implementation Notes

1. Architecture flags must be set before any code that depends on them
2. Flag settings affect code generation and optimization
3. Invalid combinations will be caught at assembly time
4. Changes to architecture flags require full reassembly

## References

1. [Mecrisp Ice: Pseudo Dual Port RAM](https://mecrisp-ice.readthedocs.io/en/latest/pseudo-dual-port.html)
   - Details about memory access patterns in different BRAM configurations
   - Explanation of pseudo dual-port RAM behavior in iCE40 FPGAs

2. [Mecrisp Ice: Instruction Set](https://mecrisp-ice.readthedocs.io/en/latest/instruction-set.html)
   - Documentation of J1 instruction set variants
   - Information about Hana 1 extensions

These references provide additional technical details about J1 implementations and FPGA-specific considerations.
