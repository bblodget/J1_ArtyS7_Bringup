# J1 Architecture Flags

This document describes the configuration flags for the J1 architecture variants supported by the assembler and the associated directive system.

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

## Directive System

The J1 assembler supports the following directive types:

### Architecture Flags Directive

Architecture flags can be specified in assembly code using the `.arch_flag` directive:

```
.arch_flag fetch_type dualport
.arch_flag alu_ops original
```

When an architecture flag is set, the assembler automatically defines a corresponding constant that can be queried:

```
ARCH_FETCH_TYPE  ( 0 = quickstore, 1 = dualport )
ARCH_ALU_OPS     ( 0 = original, 1 = extended )
```

### Constant Definition Directive

General-purpose constants can be defined using the `.define` directive:

```
.define MAX_COUNT 100
.define DEBUG_MODE 1
.define FEATURE_ENABLED 0
```

### Conditional Assembly Directives

The assembler supports conditional assembly using the following directives:

```
.if <expression>
  \ Code to include if expression is true (non-zero)
.else
  \ Code to include if expression is false (zero)
.endif
```

Additional conditional directives:

```
.ifdef CONSTANT_NAME
  \ Code included if constant is defined
.ifndef CONSTANT_NAME
  \ Code included if constant is not defined
.endif
```

## Usage Examples

### Using Architecture Flags

```
.arch_flag fetch_type dualport
\ This will automatically define ARCH_FETCH_TYPE = 1

.if ARCH_FETCH_TYPE == 1
  \ Dual-port specific code
.else
  \ Quickstore specific code
.endif
```

### Using Constants with Conditionals

```
.define STACK_SIZE 64
.define DEBUG_MODE 1

.if DEBUG_MODE
  \ Debug-only code
.endif

.if STACK_SIZE > 32
  \ Code for larger stack configurations
.endif

.ifdef CUSTOM_FEATURE
  \ Feature-specific code
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
