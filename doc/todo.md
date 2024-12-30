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
- [ ] Add proper error handling with line numbers

## Testing Infrastructure
- [x] Create test cases for:
  - [x] Basic ALU operations
  - [x] Stack operations with modifiers
  - [x] Jump instructions with labels
  - [ ] Error conditions
  - [ ] Edge cases in instruction encoding

## Documentation
- [ ] Add comments explaining instruction encoding
- [ ] Document supported syntax
- [x] Add examples in test files
- [ ] Update README.md with usage instructions

## Integration
- [ ] Merge working code into j1tools package
- [ ] Update package structure
- [ ] Add command line interface
- [ ] Add proper error messages
- [ ] Add debug output option

## Future Enhancements
- [ ] Add high-level assembly support
- [ ] Add macro support
- [ ] Add symbol table for constants
- [ ] Add listing file output
- [ ] Add binary output format

## Notes
- Start with low-level assembly support first
- Use test4 files as starting point
- Will eventually integrate into j1tools package
- Consider disassembler development after assembler is working
