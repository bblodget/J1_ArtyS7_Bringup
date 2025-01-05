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
- [x] Add command line interface improvements
  - [x] Add verbose output option
  - [x] Add listing file output
  - [x] Add symbol table output
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
    - [ ] Add +RET optimization support for comparison operations
  - [ ] Memory/IO operations (@, !, IO@, IO!)
  - [ ] System operations (DINT, EINT, DEPTH, RDEPTH)
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
- [ ] Add native negative number support
  - [ ] Update grammar to accept negative decimal literals (#-5)
  - [ ] Generate multiple instructions for negative numbers
    - #-5 should generate: #5 1- INVERT
  - [ ] Add tests for negative number handling
  - [ ] Document negative number optimization
  - [ ] Consider optimization for common negative values

- [ ] Add Forth-like syntax support
  - [ ] Support `: name` as alternative to `name:`
  - [ ] Parse stack effect comments `( ... )`
  - [ ] Handle trailing semicolons
  - [ ] Add tests for Forth syntax

- [ ] Implement INLINE directive
  - [ ] Add INLINE to grammar
  - [ ] Copy subroutine code at assembly time
  - [ ] Skip RET when inlining
  - [ ] Add tests for INLINE directive

- [ ] Add macro support
  - [ ] Add `macro:` directive to grammar
  - [ ] Implement macro expansion
  - [ ] Add tests for macro expansion
  - [ ] Document macro limitations

- [ ] Implement constant folding
  - [ ] Add simulation stack to assembler
  - [ ] Add built-in operation emulation
    - [ ] Basic arithmetic (+, -, *, /)
    - [ ] Logical operations (and, or, xor)
    - [ ] Comparisons (=, <, U<)
  - [ ] Track constant values during assembly
  - [ ] Replace operations with constants when possible
  - [ ] Add tests for constant folding
  - [ ] Document foldable operations

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
