# J1 Assembler Development Tasks

## Initial Setup
- [x] Update j1.lark grammar to support full low-level syntax
  - [x] ALU operations (T, N, T+N, etc.)
  - [x] Stack modifiers (T->N, T->R, etc.)
  - [x] Return stack deltas (r+0, r+1, r-1, r-2)
  - [x] Data stack deltas (d+0, d+1, d-1, d-2)
  - [x] Bracket syntax for modifiers [mod1,mod2,...]

## Core Assembler Features
- [x] Implement instruction encoding
  - [x] ALU operation bits (12-8)
  - [x] Stack operation bits (7-4)
  - [x] Return stack delta bits (3-2)
  - [x] Data stack delta bits (1-0)
- [x] Add support for literals (LIT)
- [x] Add support for jumps (JMP, ZJMP, CALL)
- [x] Add label resolution for jumps
- [x] Add proper error handling with line numbers

## Testing Infrastructure
- [x] Create test cases for:
  - [x] Basic ALU operations
  - [x] Stack operations with modifiers
  - [x] Jump instructions with labels
  - [x] Error conditions
  - [x] Edge cases in instruction encoding
- [x] Add test coverage reporting
- [x] Update README with testing instructions
- [X] Update firmware tests to use source *.asm and expected output *.hex

## Documentation
- [x] Add comments explaining instruction encoding
- [x] Document supported syntax
- [x] Add examples in test files
- [x] Update README.md with usage instructions
- [x] Add development setup instructions
- [x] Add testing documentation

## Integration
- [x] Merge working code into j1tools package
- [x] Update package structure
- [ ] Add command line interface improvements
  - [x] Add verbose output option
  - [ ] Add listing file output
  - [ ] Add symbol table output
- [x] Add proper error messages with line numbers
- [x] Add debug output option

## Future Enhancements
- [ ] Add high-level assembly support
- [ ] Add macro support
- [ ] Add symbol table for constants
- [ ] Add listing file output
- [ ] Add binary output format
- [ ] Add disassembler support

## High-Level Assembly Support
- [x] Implement basic high-level words
  - [x] Stack operations (DUP, DROP, SWAP, OVER, NIP, NOOP)
  - [x] Return stack operations (>R, R>, R@)
  - [x] Complete arith_test.asm
    - [x] Arithmetic operations (ADD(+), SUBTRACT(-), 1+, 1-, 2*, 2/, etc.)
    - [x] Logic operations (AND, OR, XOR, INVERT)
    - [x] Add +RET optimization support for arithmetic/logic words
  - [x] Comparison operations (=, <, U<)
    - [x] Add +RET optimization support for comparison operations
  - [x] Memory/IO operations (@, !, IO@, IO!)
  - [x] System operations (DINT, EINT, DEPTH, RDEPTH)
- [ ] Add +RET optimization support
  - [x] Identify compatible operations
  - [x] Implement suffix parsing
  - [x] Generate optimized machine code
- [ ] Implement control structures
  - [ ] IF THEN
  - [ ] IF ELSE THEN
  - [ ] BEGIN UNTIL
  - [ ] BEGIN WHILE REPEAT
- [x] Add error handling
  - [x] Stack effect validation
  - [x] Control structure validation
  - [x] Invalid +RET usage detection
- [x] Add test cases
  - [x] Basic word tests
  - [ ] Control structure tests
  - [x] +RET optimization tests
  - [x] Error condition tests
- [ ] Update documentation
  - [ ] Add examples for each control structure
  - [ ] Document stack effects
  - [ ] Document machine code mappings
  - [ ] Add error message documentation

## Assembly Optimizations
- [ ] Implement low-level constant folding
  - [ ] Identify foldable ALU operations
    - [ ] Core operations (T, N, T+N, T&N, etc.)
    - [ ] Stack operations (T->N, T->R, R->T)
    - [ ] Stack depth tracking (d+1, d-1, r+1, r-1)
  - [ ] Add simulation stack to assembler
    - [ ] Track constant values
    - [ ] Track stack depths
    - [ ] Handle R stack operations
  - [ ] Implement ALU operation emulation
    - [ ] Basic arithmetic (T+N, etc.)
    - [ ] Logical operations (T&N, T|N, T^N, ~T)
    - [ ] Shifts (N<<T, N>>T, Nu>>T)
  - [ ] Add tests for constant folding
    - [ ] Basic ALU operations
    - [ ] Stack manipulation
    - [ ] Complex macros
    - [ ] Error conditions
  - [ ] Document foldable operations
    - [ ] List supported ALU operations
    - [ ] Explain stack effects
    - [ ] Provide optimization examples

- [ ] Add macro support
  - [ ] Add `macro:` directive to grammar
  - [ ] Implement macro expansion
  - [ ] Add tests for macro expansion
  - [ ] Document macro limitations

- [ ] Implement INLINE directive
  - [ ] Add INLINE to grammar
  - [ ] Copy subroutine code at assembly time
  - [ ] Skip RET when inlining
  - [ ] Add tests for INLINE directive

- [ ] Add optimization documentation
  - [ ] Document macro usage
  - [ ] Document INLINE directive
  - [ ] Document constant folding
  - [ ] Add optimization examples

## Hardware Enhancements
- [ ] Parameter Register File
  - [x] Document concept and design
  - [ ] Implement >P(n) instruction in HDL
  - [ ] Add parameter scope management
  - [ ] Add assembler support
  - [ ] Add test cases
  - [ ] Update documentation

## Notes
- Start with low-level assembly support first
- Use test4 files as starting point
- Will eventually integrate into j1tools package
- Consider disassembler development after assembler is working

## New Feature Proposals

### Forth-like Syntax Support
- [ ] Add Forth-style function definitions (`: name ... ;`)
- [ ] Support stack effect comments `( ... -- ... )`
- [ ] Add optimization directives
  - [ ] `macro:` for simple substitutions
  - [ ] `foldable:` for compile-time computation
  - [ ] `inline:` for forced inlining
- [ ] Implement stack effect validation
- [ ] Add compatibility mode for traditional syntax

### Macro System Implementation
- [ ] Core Cleanup
  - [x] Remove high-level words from core assembler
  - [x] Update grammar for core instructions
  - [x] Simplify assembler core
- [ ] Macro Processing
  - [ ] Add `include` directive support
  - [ ] Implement macro definition parsing
  - [ ] Create macro expansion system
  - [ ] Add cycle detection for includes
- [ ] Optimization Features
  - [ ] Add constant folding support
  - [ ] Implement simulation stack
  - [ ] Add inline expansion
  - [ ] Support compile-time optimization

### Memory Sections Support
- [ ] Add basic section support
  - [ ] `.code` section
  - [ ] `.data` section
  - [ ] `.rodata` section
  - [ ] `.bss` section
- [ ] Implement section attributes
  - [ ] READONLY
  - [ ] RW (read-write)
  - [ ] NOLOAD
- [ ] Add memory configuration
  - [ ] Memory region definitions
  - [ ] Section placement controls
  - [ ] Initialization support
- [ ] Generate memory maps
  - [ ] Section usage statistics
  - [ ] Symbol locations
  - [ ] Memory layout visualization

### Development Tools
- [ ] Enhanced Debug Output
  - [ ] `--preprocess` for macro expansion
  - [ ] `--dump-ir` for internal representation
  - [ ] Stack effect verification
  - [ ] Cross-reference generation
- [ ] Memory Analysis
  - [ ] Section usage reports
  - [ ] Memory map generation
  - [ ] Symbol cross-references
- [ ] Optimization Reports
  - [ ] Constant folding results
  - [ ] Inlining decisions
  - [ ] Stack effect analysis

### j1asm Command-Line Interface
- [x] Update debug logging to use logging library
- [x] Add Click Library for CLI
- [ ] Basic Output Options
  - [x] Add `-o, --output FILE` option
  - [ ] Add `--symbols` for symbol file (.sym) generation
  - [ ] Add `--listing` for listing file (.lst) generation

- [ ] Include Path Options
  - [ ] Add `-I, --include DIR` support
  - [ ] Implement include path search order
  - [ ] Add system-wide macro library path support

- [ ] Optimization Controls
  - [ ] Add `--opt-level N` (0-3) support
  - [ ] Add `--no-fold` option
  - [ ] Add `--no-inline` option

- [ ] Debug Options
  - [x] Add `-d, --debug` support
  - [ ] Add `--preprocess, -E` for preprocessed assembly output
  - [ ] Add `--dump-ir` for intermediate representation output

- [ ] Future Enhancements
  - [ ] Add `--trace-macros` for macro expansion tracking
  - [ ] Add `--macro-path` for macro library path override
  - [ ] Add `--format=hex|bin|mif` output format selection
  - [ ] Add `--annotate` for source comment annotation
  - [ ] Add `--map` for memory map generation
  - [ ] Add `--stack-check` for stack effect verification
  - [ ] Add `--word-usage` for word usage statistics
  - [ ] Add `--cross-reference` for cross-reference generation
