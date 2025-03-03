# J1 Architecture Flags

This document describes the configuration flags for the J1 architecture variants supported by the assembler.

## Supported Architecture Variants

Currently, the assembler supports the j1a 16-bit architecture with the following configuration options:

### Memory Configuration
- **fetch_type**:
  - `quickstore` [default]: Uses the quickstore memory access pattern
  - `dualport`: Uses dual-port memory access pattern

### ALU Operations
- **alu_ops**:
  - `extended` [default]: Includes additional ALU operations beyond the original J1
  - `original`: Only includes the original J1 ALU operations

## Usage in Assembly

Architecture flags can be specified in assembly code using directives:

```
.arch_flag fetch_type dualport
.arch_flag alu_ops original
```

The assembler provides built-in constants that can be queried to determine the current architecture configuration:

```
ARCH_FETCH_TYPE  ( 0 = quickstore, 1 = dualport )
ARCH_ALU_OPS     ( 0 = original, 1 = extended )
```

Example usage in conditional assembly:

```
.if ARCH_FETCH_TYPE == 1
  \ Dual-port specific code
.else
  \ Quickstore specific code
.endif
```

## Implementation Details

### fetch_type: quickstore vs dualport

The `quickstore` configuration uses a single-port memory with a write-before-read pattern, while the `dualport` configuration uses true dual-port memory allowing simultaneous read and write operations.

### alu_ops: extended vs original

The `extended` configuration includes additional ALU operations beyond the original J1 specification:
- NlshiftT
- NrshiftT
- NarshiftT
- rstatus
- L-UM*
- H-UM*
- T+1
- T-1
- 3OS
- mem[T]

The `original` configuration includes only the basic ALU operations from the original J1 specification.
