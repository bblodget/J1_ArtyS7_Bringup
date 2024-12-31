# Development Log

## 2024-01-01

- Added support for return stack operations:
  - Implemented >R, R>, R@ instructions
  - Added correct instruction encodings:
    - >R: N [T->R,r+1,d-1] = 0x6127
    - R>: rT [T->N,r-1,d+1] = 0x6b1d
    - R@: rT [T->N,d+1] = 0x6b11
  - Updated stack_test.asm to test return stack operations
  - Added unit tests for individual return stack operations
  - Added integration test for full return stack sequence
  - Verified correct operation using simulator
- Updated documentation:
  - Marked return stack operations as completed in todo.md
  - Added return stack operation machine code mappings
  - Added stack/return-stack effect comments in test files

## 2024-12-31

- Added support for basic stack operation words:
  - Implemented DUP, DROP, SWAP, OVER, NIP, NOOP
  - Added grammar rules in j1.lark
  - Added machine code generation in asm.py
  - Created stack_test.asm example program
  - Added unit tests for individual stack operations
  - Added integration test for stack_test.asm
- Updated documentation:
  - Marked completed items in todo.md
  - Added stack operation machine code mappings
  - Added stack effect comments in test files
- Added test coverage for stack operations:
  - Individual operation tests
  - Full program test
  - Error handling for invalid operations

## 2024-12-30

- Added test coverage reporting
- Added test cases for:
  - Basic ALU operations
  - Stack operations with modifiers
  - Jump instructions with labels
  - Error conditions
  - Edge cases in instruction encoding
- Fixed error handling in tests to properly catch both ValueError and VisitError
- Updated README.md with comprehensive testing documentation
- Fixed ALU operation encoding for N[d-1] instruction
- Verified correct label resolution in add_test.asm
- Added proper error messages for undefined and duplicate labels
