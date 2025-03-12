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

## Implementation Phases

### Phase 1: Architecture Flag Directives & Basic Constants (Completed)
**Objective**: Implement `.arch_flag` with auto-defined constants

#### Tasks:
- **Grammar Updates (j1.lark)**
  - Add ARCH_FLAG token and directive rule
  - Add basic constant expression support
- **Assembler Core (asm.py)**
  - Add architecture flag storage
  - Auto-define ARCH_* constants
  - Add basic error checking for valid flags/values
- **Testing**
  - Verify flag persistence through includes
  - Test ARCH_* constant availability
  - Validate flag validation errors

### Phase 2: .define Directive & Constant System
**Objective**: Implement general constant definitions

#### Tasks:
- **Grammar Updates**
  - Add DEFINE token and rule
  - Enhance expression parser
- **Assembler Core**
  - Create constant symbol table
  - Implement constant substitution
  - Add arithmetic expression evaluation
- **Testing**
  - Test numeric constant substitution
  - Verify expression evaluation
  - Check constant scope rules

### Phase 3: Conditional Assembly Foundation
**Objective**: Implement basic `.if`/`.endif` with constants

#### Tasks:
- **Grammar Updates**
  - Add CONDITIONAL tokens
  - Add conditional block rules
- **Assembler Core**
  - Create conditional stack
  - Implement expression evaluation
  - Add code inclusion/exclusion
- **Testing**
  - Test basic conditionals with constants
  - Verify nested conditionals
  - Check error handling for missing `.endif`

### Phase 4: Advanced Conditionals
**Objective**: Add `.else`, `.ifdef`, `.ifndef`

#### Tasks:
- **Grammar Updates**
  - Add ELSE token
  - Add ifdef/ifndef rules
- **Assembler Core**
  - Implement else handling
  - Add defined() check function
  - Enhance expression parser
- **Testing**
  - Test else branches
  - Verify ifdef/ifndef behavior
  - Check complex expressions

### Phase 5: Architecture Validation
**Objective**: Enforce flag-appropriate operations

#### Tasks:
- **Assembler Core**
  - Add operation validation by architecture
  - Create flag/operation matrix
  - Implement validation errors
- **Macro System**
  - Update standard library macros
  - Add architecture-specific macros
- **Testing**
  - Verify prohibited operations throw errors
  - Test dualport/quickstore differences
  - Validate extended vs original ALU sets

### Phase 6: Integration & Validation
**Objective**: Final system testing

#### Tasks:
- **Test Suite**
  - Add architecture matrix tests
  - Create conditional stress tests
  - Verify backward compatibility
- **Documentation**
  - Update macro documentation
  - Add architecture flag examples
  - Create conditional usage guide
- **Performance**
  - Benchmark conditional overhead
  - Optimize constant resolution
  - Profile memory usage
