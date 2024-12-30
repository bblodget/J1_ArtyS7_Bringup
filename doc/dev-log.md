# Development Log

## 2024-12-31

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
