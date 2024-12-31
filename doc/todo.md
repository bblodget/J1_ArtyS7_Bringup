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
  - [ ] Add verbose output option
  - [ ] Add listing file output
  - [ ] Add symbol table output
- [ ] Add proper error messages with line numbers
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
  - [ ] Return stack operations (>R, R>, R@)
  - [ ] Arithmetic operations (+, -, 1+, 1-, 2*, 2/, etc.)
  - [ ] Logic operations (AND, OR, XOR, INVERT)
  - [ ] Comparison operations (=, <, U<)
  - [ ] Memory/IO operations (@, !, IO@, IO!)
  - [ ] System operations (DINT, EINT, DEPTH, RDEPTH)
- [ ] Add +RET optimization support
  - [ ] Identify compatible operations
  - [ ] Implement suffix parsing
  - [ ] Generate optimized machine code
- [ ] Implement control structures
  - [ ] IF THEN
  - [ ] IF ELSE THEN
  - [ ] BEGIN UNTIL
  - [ ] BEGIN WHILE REPEAT
- [ ] Add error handling
  - [ ] Stack effect validation
  - [ ] Control structure validation
  - [ ] Invalid +RET usage detection
- [ ] Add test cases
  - [x] Basic word tests
  - [ ] Control structure tests
  - [ ] +RET optimization tests
  - [ ] Error condition tests
- [ ] Update documentation
  - [ ] Add examples for each control structure
  - [ ] Document stack effects
  - [ ] Document machine code mappings
  - [ ] Add error message documentation

## Notes
- Start with low-level assembly support first
- Use test4 files as starting point
- Will eventually integrate into j1tools package
- Consider disassembler development after assembler is working
