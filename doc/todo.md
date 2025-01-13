# J1 Assembler Development Tasks

## Completed Features
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
  - [x] Nested macro support
    - [x] Expansion tracking
    - [x] Error handling
    - [x] Stack effect validation
  - [x] Include File Support
    - [x] Add 'include' keyword to grammar
    - [x] Implement include file processing
    - [x] Handle nested includes
    - [x] Test with macro libraries
  - [x] Include Path Support
    - [x] Add include path search
    - [x] Test with macro libraries in different directories
    - [x] Add standard library structure
    - [x] Implement --no-stdlib option

- [x] CLI Features
  - [x] Include Path Support
    - [x] `-I, --include DIR`
    - [x] Include search order
    - [x] Macro library path
    - [x] `--no-stdlib` option

## Current Development Focus

### Standard Library Development
- [ ] Core Word Library
  - [ ] Document all J1 ALU operations
  - [ ] Create macros for all single-instruction operations
  - [ ] Add stack effect documentation
  - [ ] Add operation descriptions
  - [ ] Test coverage for all operations
- [ ] Organization
  - [ ] Group operations by type (ALU, stack, etc)
  - [ ] Create index/reference document
  - [ ] Add usage examples

### CLI Enhancements
- [ ] Optimization Controls
  - [ ] `--opt-level N`
  - [ ] `--no-fold`, `--no-inline`
- [ ] Debug Options
  - [ ] `--preprocess`
  - [ ] `--dump-ir`
  - [ ] `--trace-macros`

### Macro System Enhancements
- [ ] Improve listing file
  - [ ] Show macro chain in comments. // (macro: 2dup.over) 
  - [ ] Provide filename somehow. Give each file a number for reference?
- [ ] Macro Parameters
  - [ ] Parameter syntax definition
  - [ ] Parameter substitution
  - [ ] Test coverage

### High-Level Assembly Support
- [ ] Case insensitive keywords
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
- Focus on macro parameters next
- Consider parameter register file implementation
- Plan for disassembler development