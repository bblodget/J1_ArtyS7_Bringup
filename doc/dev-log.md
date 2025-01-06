# Development Log

## 2025-01-05

### feature/forth-macros Branch

- Created new branch `feature/forth-macros`:
  - Simplified core assembler to focus on fundamental J1 instructions
  - Removed high-level word implementations from core assembler
  - Fixed label handling and resolution system
  - Added comprehensive test suite for core functionality
  - Documented feature plan in `feature_forth_macros.md`

- Fixed label handling in assembler:
  - Properly track label addresses during first pass
  - Correctly resolve jump targets in second pass
  - Fixed issue with label-instruction pairing
  - Added proper error handling for undefined/duplicate labels
  - Verified with comprehensive test suite

- Added test coverage for core assembler features:
  - Basic ALU operations (T, N, T+N, etc.)
  - Stack effect modifiers (T->N, T->R, etc.)
  - Stack delta modifiers (d+1, d-1, r+1, r-1)
  - Jump instructions with label resolution
  - Number literals (decimal and hex)
  - Error handling (invalid syntax, undefined labels)
  - Combined modifiers (ALU + stack effects)
  - All 39 tests passing successfully

- Improved debug output:
  - Added token display for better parsing visibility
  - Added statement processing tracking
  - Added label resolution debugging
  - Improved error messages with line/column info
  - Added instruction encoding display

- Verified correct operation of core instructions:
  - Label resolution for forward/backward jumps
  - Stack effect combinations
  - ALU operations with modifiers
  - Memory and IO operations
  - Return stack operations
  - System operations (DINT, EINT)

- Documented macro system design:
  - Created feature specification in `feature_forth_macros.md`
  - Defined implementation phases:
    1. Core cleanup (completed)
    2. Macro system implementation (next)
    3. Optimization features (planned)
  - Specified file structure and CLI enhancements
  - Detailed testing strategy and migration path
  - Added examples of macro usage and optimization

### Main Branch

- Added support for Memory/IO operations:
  - Implemented @ (fetch) operation: `mem[T] [T->N]`
  - Implemented ! (store) operation: `T [N->[T],d-2]`
  - Implemented IO@ operation: `io[T] [IORD]`
  - Implemented IO! operation: `T [N->io[T],d-2]`
  - Added +RET variants for all memory/IO operations:
    - @+RET: `mem[T] [T->N,RET,r-1]`
    - !+RET: `T [N->[T],RET,d-2,r-1]`
    - IO@+RET: `io[T] [IORD,RET,r-1]`
    - IO!+RET: `T [N->io[T],RET,d-2,r-1]`

- Added support for System operations:
  - Implemented DINT (Disable Interrupts): `T [fDINT]`
  - Implemented EINT (Enable Interrupts): `T [fEINT]`
  - Implemented DEPTH (Data Stack Depth): `status [T->N,d+1]`
  - Implemented RDEPTH (Return Stack Depth): `rstatus [T->N,d+1]`

- Added test coverage for comparison operations with RET:
  - Created comparison_ret_test.asm test file
  - Added test cases for =+RET, <+RET, and U<+RET operations
  - Verified correct machine code generation:
    - =+RET: `0x678F` (N==T [T->N,d-1,r-1])
    - <+RET: `0x688F` (N<T [T->N,d-1,r-1])
    - U<+RET: `0x6F8F` (Nu<T [T->N,d-1,r-1])
  - Added test to test_assembler.py test suite
  - Confirmed proper stack effects (d-1,r-1)
  - Verified correct operation for both true (-1) and false (0) cases
  - Tested signed vs unsigned comparisons
  - Validated proper handling of negative numbers

## 2025-01-04

- Added support for arithmetic/logic operations with RET:
  - Implemented +RET suffix for all arithmetic operations
  - Added support for both forms (e.g., `ADD+RET` and `++RET`)
  - Added machine code generation for combined operations
  - Created comprehensive test program `arith_ret_test.asm`
  - Verified correct operation using simulator

- Added instruction encodings for arithmetic+RET operations:
  - ADD+RET/++RET: `0x628F` (T+N [T->N,d-1,r-1])
  - SUBTRACT+RET/-+RET: `0x6C8F` (N-T [T->N,d-1,r-1])
  - AND+RET: `0x638F` (T&N [T->N,d-1,r-1])
  - OR+RET: `0x648F` (T|N [T->N,d-1,r-1])
  - XOR+RET: `0x658F` (T^N [T->N,d-1,r-1])
  - INVERT+RET: `0x668C` (~T [T->N,r-1])
  - 1++RET: `0x768C` (T+1 [T->N,r-1])
  - 1-+RET: `0x778C` (T-1 [T->N,r-1])
  - 2*+RET: `0x6A8C` (<< [T->N,r-1])
  - 2/+RET: `0x698C` (>> [T->N,r-1])

- Grammar improvements:
  - Added RET_SUFFIX token for +RET combinations
  - Limited +RET suffix to arithmetic/logic operations only
  - Maintained proper error handling for invalid combinations
  - Verified clear error messages with line number and context

- Updated test suite:
  - Added arith_ret_test.asm to test coverage
  - Verified all arithmetic+RET operations generate correct machine code
  - Confirmed proper error handling for invalid combinations
  - All 58 tests passing successfully

- Documented parameter register file concept:
  - Proposed enhancement for quick access to frequently used parameters
  - Detailed instruction encoding for >P(n) operation
  - Explored parameter scope management approaches using BRAM or base pointer
  - Documented integration with return stack for automatic context management
  - Provided example usage in Forth with clean parameter handling

- Added support for comparison operations:
  - Implemented =, <, and U< comparison operators
  - Added proper instruction encodings:
    - = (N==T): `0x6703` (N==T [d-1])
    - < (N<T): `0x6803` (N<T [d-1])
    - U< (Nu<T): `0x6F03` (Nu<T [d-1])
  - Still TODO: add +RET variants for subroutine returns:
    - =+RET: `0x678F` (N==T [T->N,d-1,r-1])
    - <+RET: `0x688F` (N<T [T->N,d-1,r-1])
    - U<+RET: `0x6F8F` (Nu<T [T->N,d-1,r-1])
  - Created comparison_test.asm to verify operations
  - Added test suite coverage for comparison operations
  - Documented proper handling of signed comparisons with negative numbers

## 2025-01-03

- Resolved issues with ALU operation parsing:
  - Adjusted the grammar in `j1.lark` to prioritize combined ALU operations (e.g., `T+N`) over standalone operators (`+`).
  - Specified priority for terminal tokens using the notation `TERM.number`, allowing `T_PLUS_N.2` and `N_MINUS_T.2` to match before the raw `ADD` and `SUBTRACT` words.
  - Reintroduced standalone `+` and `-` operators in the grammar without conflicts.

- Conducted extensive testing:
  - Ran the test suite, resulting in all 45 tests passing successfully.
  - Confirmed that the assembler correctly processes ALU operations without errors.

- Updated firmware tests to use source *.asm and expected output *.hex.

- **Learned about handling negative numbers on the stack**:
  - To push negative values onto the data stack, one can load a positive value and then use the `INVERT` instruction. For example, to push `-2`, load `$0002`, subtract `1` using `1-`, and then apply `INVERT`, resulting in `0xFFFE` on the stack.

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
