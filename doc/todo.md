# J1 Assembler Development Tasks

## Completed Core Features
- [x] Initial Grammar and Syntax
  - [x] ALU operations, stack modifiers, stack deltas
  - [x] Instruction encoding (ALU, stack, return stack, data stack bits)
  - [x] Support for literals, jumps, and labels
  - [x] Basic error handling with line numbers

- [x] Macro System
  - [x] Core macro implementation (`macro:` directive)
  - [x] Macro expansion and cycle detection
  - [x] Basic test coverage
  - [x] Documentation
  - [x] Add a macro column to the listing file
  - [x] More refactoring of asm.py
  - [x] Update listing so any comments are aligned in a column
  - [x] Test with macros with no comments
  - [x] Test with single line macros
  - [x] Preserve full instruction text in macro expansion

## Current Development Focus

### Macro System Enhancements
- [ ] Macro Parameters
  - [ ] Parameter syntax definition
  - [ ] Parameter substitution
  - [ ] Test coverage
- [ ] Nested Macro Support
  - [ ] Expansion tracking
  - [ ] Error handling
  - [ ] Stack effect validation

### High-Level Assembly Support
- [ ] Control Structures
  - [ ] IF THEN
  - [ ] IF ELSE THEN
  - [ ] BEGIN UNTIL
  - [ ] BEGIN WHILE REPEAT
- [ ] Documentation
  - [ ] Control structure examples
  - [ ] Stack effect documentation
  - [ ] Machine code mappings

### Optimization Features
- [ ] Constant Folding
  - [ ] ALU operation folding
  - [ ] Stack simulation
  - [ ] Test coverage
- [ ] INLINE Directive
  - [ ] Grammar and implementation
  - [ ] Subroutine inlining
  - [ ] Testing

### Memory Management
- [ ] Section Support
  - [ ] Basic sections (.code, .data, .rodata, .bss)
  - [ ] Section attributes
  - [ ] Memory configuration
- [ ] Memory Analysis
  - [ ] Usage reports
  - [ ] Symbol cross-references
  - [ ] Memory maps

### CLI Enhancements
- [ ] Include Path Support
  - [ ] `-I, --include DIR`
  - [ ] Include search order
  - [ ] Macro library path
- [ ] Optimization Controls
  - [ ] `--opt-level N`
  - [ ] `--no-fold`, `--no-inline`
- [ ] Debug Options
  - [ ] `--preprocess`
  - [ ] `--dump-ir`
  - [ ] `--trace-macros`

### Hardware Features
- [ ] Parameter Register File
  - [ ] >P(n) instruction
  - [ ] Parameter scope management
  - [ ] Assembler support

## Future Enhancements
- [ ] Forth-like Syntax
  - [ ] Function definitions (`: name ... ;`)
  - [ ] Stack effect validation
  - [ ] Optimization directives
- [ ] Binary Output Support
- [ ] Disassembler
- [ ] Advanced Memory Features
  - [ ] Memory initialization
  - [ ] Section placement controls

## Project Management
- [ ] Licensing
  - [ ] Add SwapForth license to 3rd party licenses
  - [ ] Create LICENSE file
  - [ ] Add copyright notices to source files

## Notes
- Focus on macro parameters and nested macros next
- Consider parameter register file implementation
- Plan for disassembler development