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
  - [x] Nested macro support
    - [x] Expansion tracking
    - [x] Error handling
    - [x] Stack effect validation
  - [x] Include File Support
    - [x] Add 'include' keyword to grammar
    - [x] Implement include file processing
    - [x] Handle nested includes
    - [x] Test with macro libraries

## Current Development Focus

### Macro System Enhancements
- [ ] Include Path Support
  - [ ] Add include path search
  - [ ] Test with macro libraries in different directories
- [ ] Improve listing file.
  - [ ] Show macro chain in comments. // (macro: 2dup.over) 
  - [ ] Provide filename somehow.  Give each file a number for reference?
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
- Focus on include path support and macro parameters next
- Consider parameter register file implementation
- Plan for disassembler development