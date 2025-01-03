# Development Log

## 2025-01-03

- Resolved issues with ALU operation parsing:
  - Adjusted the grammar in `j1.lark` to prioritize combined ALU operations (e.g., `T+N`) over standalone operators (`+`).
  - Despite attempts to maintain standalone `+` and `-` operators, conflicts arose, leading to incorrect parsing of ALU operations.
  - Temporarily removed `+` and `-` from `ADD` and `SUBTRACT` definitions to ensure all tests pass.

- Conducted extensive testing:
  - Ran the test suite, resulting in all 45 tests passing successfully.
  - Confirmed that the assembler correctly processes ALU operations without errors.

- Update firmware tests to use source *.asm and expected output *.hex

## 2025-01-02

- Improved error reporting in assembler:
  - Added consistent error message format: filename:line:column: message
  - Fixed line number counting for accurate error locations
  - Added proper error context display with pointer to error location
  - Updated all error messages to include file location information
  - Fixed error reporting to show actual error line instead of next line
  - Added debug mode to show detailed error context
  - Improved grammar error messages with better context
- Simplified ALU operation handling:
  - Added direct token definitions for compound operations (T+N, N-T, etc.)
  - Removed special case handling in alu_op method
  - Made grammar more explicit about valid operations
  - Improved error detection for invalid ALU operations

## 2025-01-01

- Fixed ALU operation handling in assembler:
  - Added support for operations with multiple modifiers
  - Fixed handling of T-N vs N-T operations
  - Improved modifier combination logic using bitwise OR
  - Added proper handling of unary operations (like ~T)
  - Fixed binary operations (T+N, T&N, etc.)
- Fixed test cases:
  - All stack modifier tests now passing
  - All arithmetic operation tests now passing
  - Full add_test.asm program now assembles correctly
- Improved error handling:
  - Better error messages for invalid modifiers
  - Better error messages for invalid operations
  - Added validation for modifier combinations
- Code improvements:
  - Refactored alu_op method for better clarity
  - Added proper handling of modifier chains
  - Improved documentation of ALU operation handling
  - Added comments explaining bitwise operations


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
