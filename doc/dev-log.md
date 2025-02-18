# Development Log

## 2025-02-18

- Added 1+ and 1- macros to j1_base_macros.asm
- Added raw_loop test case to tests/test_files/control/raw_loop

Refactor DO LOOP implementation with improved instruction generation

- Updated DO LOOP transformation in asm.py with more precise instruction generation
- Corrected stack and register effects for loop control instructions
- Replaced 2dup with over over for stack manipulation
- Adjusted test cases to use a smaller loop limit (3 instead of 5)
- Improved instruction text and metadata for better readability


## 2025-02-17

Add raw loop test case for basic DO LOOP implementation.
We created this test case to help debug the DO LOOP implementation,
which is not working in the simulator.

- Created test files for a simple raw loop in j1 assembly
- Added Makefile for compiling and debugging the test case
- Implemented a basic DO LOOP with fixed increment and limit
- Included hex file for the raw loop test


## 2025-02-16

Implement DO LOOP control structure

- Added DO LOOP grammar rules to j1.lark
- Implemented do_loop method in asm.py for transforming DO LOOP constructs
- Created test case for basic DO LOOP
- Added documentation for DO LOOP implementation plan
- Updated todo.md with DO LOOP implementation tasks
- Prepared refactoring plan for future code organization

Add loop index access macros and nested DO LOOP test case

- Introduced `i`, `j`, and `k` macros in j1_base_macros.asm for accessing loop indices
- Created nested DO LOOP test case with multiple loop levels
- Updated test_assembler.py to include nested_do_loop test
- Added Makefile and test assembly file for nested DO LOOP

Enhance DO LOOP context tracking and warning system

- Implemented robust loop context tracking with depth tracking for nested DO LOOPs
- Added comprehensive warning system for loop index words (i, j, k)
- Updated assembler to track loop nesting and provide context-aware warnings
- Created test case `warn_ijk` to validate loop index word usage rules
- Modified grammar to support more granular DO LOOP processing

Implement +LOOP control structure for DO loops

- Added support for DO +LOOP with variable increments
- Implemented complex transformation handling positive and negative increments
- Updated grammar to distinguish DO LOOP and DO +LOOP
- Created test cases for DO +LOOP with positive and negative increments
- Added negation macro for handling negative loop increments
- Extended assembler to generate correct loop control flow for +LOOP


## 2025-02-15

- Created new nested_if_then test case
- Refactored IF THEN control structure to use new `if_then` rule
- Refactored the `if_else_then` rule and method
- Created the `loop_until` rule and method and test case
- Created the `nested_loop_until` test case
- Created the `loop_while` rule and method and test case



## 2025-02-14

- Updated IF ELSE THEN control structure implementation:
  - Modified the `else_op` method in `asm.py` to emit an unconditional JMP **before** generating the false branch label.
  - Ensured that the false branch label now appears after the JMP, providing correct backpatching for control flow.
  - Verified via symbol and listing outputs that labels (e.g., `if_false_0` and `if_end_1`) are correctly ordered.
  - Tested with `if_else_then.asm` to confirm that for a true condition, the false branch is skipped, and for a false condition, the false branch is executed.

## 2025-02-13

- Implemented Forth-style IF/THEN control structures:
  - Added IF and THEN tokens to grammar
  - Removed old if_then rule in favor of separate if_op and then_op rules
  - IF generates ZJMP instruction with unique label
  - THEN generates label marker for backpatching
  - Added if_stack to track nested IF/THEN pairs
  - Updated listing output to show:
    - ZJMP instructions with target labels
    - Label markers at correct word addresses
  - Verified correct bytecode generation
  - Added test case (if_then.asm) demonstrating:
    - True condition branch execution
    - False condition branch skipping
    - Proper label resolution
    - Correct word addressing

## 2025-02-12

- Added THEN operation to support conditional jumps.
- Added IF operation to support conditional jumps.
- Added test cases for IF and THEN operations.
- Byte code looks correct.
- TODO: Fix missing labels in listing file.

## 2025-02-09

- Fixed subroutine definition to use the word address of the first instruction in the body as the subroutine label address.
- Added ORG directive to set the starting address of the next instruction.
- All test passing.
- Added ability to call subroutines using bare identifiers.
- Added call_expr.md documentation.
- Added io_words.asm to io_lib to test calling subroutines.

## 2025-02-04

Planning for ORG and SECTIONS directives.
- [sections_simplified.md](sections_simplified.md)
- [ORG_command.md](ORG_command.md)
- [org_section_plan.md](org_section_plan.md)

## 2025-02-03

Enhanced listing output:
- Added byte address column to listing output
- Maintained word address column for instruction references
- Aligned all columns for better readability
- Updated column headers to match data alignment
- Preserved existing functionality:
  - Label formatting
  - Macro expansion annotations
  - Source line comments
  - Line and column numbers
- Reused and enhanced generate_listing_line method
- Extended separator line to match wider format

Example output now shows:
```
BYTE     WORD     CODE            #:col    SOURCE
----------------------------------------------------------------------
0000     0000     0021            9:1      JMP start                    //
```
- BYTE column shows memory-mapped addresses (0000, 0002, etc.)
- WORD column shows instruction addresses (0000, 0001, etc.)
- Maintains all previous information and formatting

## 2025-02-02

Completed:
- Reverted code back to have a subroutine_def method in the asm.py file.
Instead of having a subroutine_processor.py file.
- Merge this code back into the main branch.
- Basic subroutine definition and call implemented.

Next Steps:
- enhance listing output. Show both byte and word addresses.
- Implement ORG directive.
- Subroutine call syntax. Allow direct subroutine names as CALL targets

## 2025-01-18

- Debugged UART I/O library (terminal_io.asm):
  - Fixed stack manipulation issues in UART status checking
  - Identified incorrect `over` usage in `emit?` function
  - Found simulator always returns 0xF for UART status (0x2000)
  - Simplified `uartstat` function implementation
  - Tested basic I/O functionality:
    - Character output working (`emit`)
    - Character input working (`key`)
    - Two-character output working (`2emit`)
    - Echo test functioning but unrealistic due to simulator

- Fixed assembler unresolved jump handling:
  - Modified to warn about unresolved jumps in included files
  - Maintained strict checking for main file
  - Added main file tracking in assembler
  - Preserved all test cases (54 passing)
  - Improved error reporting for undefined labels

- Next steps:
  1. Improve simulator UART status behavior
  2. Remove temporary JMP start from library files
  3. Add proper entry point handling
  4. Consider adding string output capabilities

## 2025-01-17

- Finished refactoring test_assembler.py
    - Added test_files/macros/base_status
    - Added test_files/macros/base_rstack
    - Added test_files/macros/base_io
    - Added test_files/macros/base_elided
    - Added test_files/macros/base_dup_over
    - Added test_files/macros/base_compare
    - Added test_files/macros/base_alu

## 2025-01-16

- Reorganized test files structure:
  - Moved test files from firmware/ to j1tools/tests/test_files/
  - Created organized category directories:
    - arith/ (test_add_subroutine, test_basic_ops)
    - include/ (test_basic_include, test_nested_include)
    - macros/ (test_macros_basic, test_macros_words, test_j1_base_macros)
    - memory/ (test_memory)
  - Preserved all .asm, .hex, and Makefile files
  - Created migration script (migrate_tests.py)

- Refactored test_assembler.py:
  - Simplified test program handling using parameterized tests
  - Removed redundant test fixtures and methods
  - Created single parameterized test_program function
  - Maintained special case handling for include tests
  - Updated file paths to use new test_files structure
  - Verified all 47 tests passing successfully

- Benefits of new structure:
  - Cleaner separation of test files from firmware
  - Better organization by test category
  - Easier to add new tests
  - More maintainable test code
  - Proper Python project structure
  - Clear test output with category/name identification

- Next steps:
 - Cleanup test_files/macros/test_j1_base_macros
 - Add these tests to the test_assembler.py

## 2025-01-14

- Fixed identifier pattern matching in j1.lark grammar:
  - Added support for Forth-style compound identifiers
  - Updated IDENT patterns to handle:
    - Basic identifiers with optional special char suffix (`swap`, `u<`)
    - Pure operator sequences (`+`, `-`)
    - Number-operator combinations (`2*`, `2/`)
    - Special char prefix with letters (`>r`, `r@`)
    - Special char infix identifiers (`dup>r`)
    - Added support for `@` and `!` operators
  - Verified all patterns with test_platform.asm

- Created comprehensive test platform:
  - Implemented test_platform.asm with full coverage:
    - Basic stack operations (dup, drop, swap, over, nip)
    - ALU operations (+, -, and, or, xor, invert)
    - Comparison operations (u<, <, =)
    - Shift operations (2*, 2/)
  - Verified correct machine code generation
  - Added detailed stack effect comments
  - Confirmed proper listing file generation

- Validated assembler functionality:
  - Tested macro expansion with complex identifiers
  - Verified correct source line tracking
  - Confirmed proper machine code generation
  - Validated listing file format and comments
  - Tested symbol file generation

- Next steps:
  1. Add tests for return stack operations (>r, r>, r@)
  2. Implement I/O operation tests (io@, io!)
  3. Add status operation tests (depth, exit, dint, eint)
  4. Consider adding multi-instruction macro support

### Afternoon 2025-01-14

- Implemented and tested basic I/O operations:
  - Created test_io.asm to verify I/O functionality:
    - UART write at 0x1000 (verified with ASCII 'H')
    - Status register read at 0x2000 (busy/valid bits)
    - UART read at 0x1000
    - Ticks counter read at 0x4000
    - Cycles counter read at 0x8000
  - Verified address access above 0x7FFF using invert trick
  - Confirmed correct machine code generation for I/O instructions
  - Tested in simulator with expected results

- Fixed test_dup_over.asm stack effect comments:
  - Corrected expectations for overu> operation
  - Updated comments to show correct stack effects
  - Verified proper operation in simulator

- Validated I/O address decoding in hardware:
  - UART_ADDR (0x1000) for TX/RX
  - MISC_IN_ADDR (0x2000) for status
  - TICKS_ADDR (0x4000) for counter/control
  - CYCLES_ADDR (0x8000) for cycle counting
  - Confirmed proper address selection logic
  - Verified read/write enable generation

- Next steps:
  1. Test UART timing on actual hardware
  2. Implement interrupt handling for ticks overflow
  3. Add more comprehensive UART test cases
  4. Consider adding ticks counter write tests

## 2025-01-13

- Organized J1 macro libraries into logical groups:
  - Created core/j1_base_macros.asm for fundamental operations
  - Created core/j1_dualport_macros.asm for memory operations
  - Created core/j1_extended_macros.asm for HX8K-specific operations
  - Created platforms/j1_16kb_dualport.asm for platform configuration

- Improved macro organization:
  - Removed duplicate macros between files
  - Properly categorized operations based on ALU capabilities:
    - Base (0x0000-0x0F00): stack, basic ALU, I/O, status
    - Extended (0x1000-0x1900): shifts, multiply, inc/dec
    - Dualport: memory operations using mem[T] and 3OS
  - Added clear stack effect comments
  - Grouped related operations together

- Created initial test platform:
  - Added firmware/test_platform/test_platform.asm
  - Structured to test all macro categories
  - Identified grammar issue with operator symbols (+, -, etc.)
  - TODO: Update grammar to support operator symbols in macro names

- Discovered implementation insights:
  - Confirmed 16KB variant works with 8KB (4K words) memory
  - Extended instruction set provides optimization opportunities
  - Dual-port operations available with single BRAM implementation

- Next steps:
  1. Update grammar to support operator symbols in macro names
  2. Complete test platform implementation
  3. Add comprehensive test cases for all macro categories
  4. Consider adding platform-specific configuration options

## 2025-01-12

- Fixed nested macro expansion and include processing:
    - Updated MacroProcessor to use proper MacroDefinition class
    - Fixed macro body handling for nested expansions
    - Ensured correct source line tracking through macro expansion
    - Example working with nested includes and macros:
        ```forth
        // Core word
        macro: over ( a b -- a b a ) N[T->N,d+1] ;

        // Complex macro using core word
        macro: 2dup ( a b -- a b a b )
            over
            over
        ;
        ```

- Improved macro expansion handling:
    - Added proper flattening of nested macro instructions
    - Maintained correct source attribution in listing file
    - Preserved macro names in expanded instructions
    - Example listing output shows proper expansion:
        ```
        0002     6111            6:5      N[T->N,d+1]                     //  (macro: 2dup)
        0003     6111            6:5      N[T->N,d+1]                     //  (macro: 2dup)
        ```

- Enhanced include file processing:
    - Fixed nested include file handling
    - Maintained proper file context for error messages
    - Tracked macro definitions across included files
    - Example include chain working:
        ```
        test_nested_include.asm
          -> math/math_words.asm
              -> core/core_words.asm
        ```

- Implemented standard library organization:
    - Created standard library directory structure:
        ```
        lib/
        ├── core/           # Core Forth words
        ├── math/           # Math operations
        └── string/         # Future string ops
        ```
    - Added core_words.asm with basic stack operations
    - Added math_words.asm with arithmetic operations
    - Verified nested includes across library files

- Enhanced include path handling:
    - Added --include (-I) option for additional search paths
    - Added --no-stdlib option to disable standard library
    - Implemented proper include path search order:
        1. Current directory
        2. Explicit include paths (-I)
        3. Standard library (unless disabled)
    - Added comprehensive tests:
        - Basic file inclusion
        - Stdlib access
        - Include path precedence
        - Error conditions

- Test Coverage:
    - Verified nested macro expansion with test_nested_include.asm
    - Confirmed correct machine code generation:
        - Stack manipulation (dup, drop, swap, over)
        - ALU operations (T+N)
        - Control flow (JMP)
    - Validated listing file shows proper macro attribution
    - Tested include file processing with multiple levels
    - Added tests for include path search order
    - Verified stdlib disable/enable functionality

## 2025-01-11

- Refactored assembler types and modifier handling:
    - Renamed instruction_metadata.py to asm_types.py
    - Added new dataclasses for modifier handling:
        - Modifier: value, text, token
        - ModifierList: combined value, text, tokens
    - Added comprehensive type hints to asm.py and macro_processor.py
    - Improved error reporting with source context

- Fixed macro expansion text preservation:
    - Modified expand_macro to preserve full instruction text
    - Updated alu_op to handle ModifierList cleanly
    - Ensured modifiers show in listing file output
    - Fixed multiple modifier text combination
    - Example: "T[T->N,d+1]" instead of just "T"

- Improved code organization:
    - Moved all type definitions to asm_types.py
    - Added proper type hints to all major methods
    - Simplified modifier processing chain:
        1. modifier() -> Modifier
        2. modifier_list() -> ModifierList
        3. modifiers() -> ModifierList
        4. alu_op() -> InstructionMetadata

- Test Coverage:
    - Verified macro expansion with test_macros_words.asm
    - Confirmed correct machine code generation
    - Validated listing file format improvements:
        - Full instruction text with modifiers
        - Proper macro attribution in comments
        - Correct address and machine code values
    - Example output shows proper formatting:
        ```
        0002     6011           15:5      T[T->N,d+1]                     //  (macro: dup)
        0003     6103           16:5      N[d-1]                          //  (macro: drop)
        0005     6000           20:5      T[d+0]                          //  (macro: noop)
        ```

- Next Steps:
    1. Consider adding more complex macro test cases
    2. Look into macro parameter support
    3. Plan nested macro expansion implementation
    4. Review optimization opportunities

## 2025-01-10

- Enhanced macro processing in the assembler:
    - Fixed issues with macro expansion and instruction handling.
    - Ensured proper source line tracking for macro-expanded instructions.
    - Improved error handling and logging for macro-related errors.
    - Added label information back to the listing file output.
    - Verified correct listing output format with labels and macro annotations.

- Updated the `generate_listing` method:
    - Included label information in the listing file.
    - Ensured labels are displayed with "----" in the machine code column.
    - Added macro name annotations in the source comments for expanded instructions.

- Test Coverage:
    - Verified macro expansion and label handling with `test_macros.asm`.
    - Confirmed correct machine code generation and listing file output.
    - Ensured no crashes or errors during the assembly process.

- Added InstructionMetadata class:
    - Created new class to encapsulate instruction information
    - Added fields for:
        - Instruction type (BYTE_CODE, LABEL, JUMP, MACRO_DEF, MACRO_CALL, ALU)
        - Value (bytecode/machine code)
        - Source information (filename, line, column)
        - Complete source line
        - Optional metadata (macro_name, opt_name, label_name)
    - Added factory method from_token() for easy creation
    - Updated all assembler methods to use InstructionMetadata
    - Refactored instruction handling to use metadata dictionaries:
        - instruction_metadata for regular instructions
        - label_metadata for labels
    - Improved error reporting with source context

- Improved listing file formatting:
    - Left-aligned labels for better readability
    - Indented code under labels by 2 spaces
    - Aligned all comments to consistent column
    - Fixed line:col field width for consistent alignment
    - Added macro annotations to comment field
    - Verified format with test files:
        - Labels start at column 0
        - Code indented under labels
        - Comments aligned regardless of source type
        - Line:col information properly formatted
        - Macro expansions clearly annotated

- Test Coverage:
    - Verified label and code alignment
    - Checked comment alignment with various source types
    - Confirmed macro expansion annotations
    - Tested with multiple labels and instructions
    - Validated line:col formatting
    - Tested InstructionMetadata with various instruction types
    - Verified proper metadata propagation through macro expansion

- Next Steps:
    1. Add more complex macro test cases.
    2. Consider adding macro parameter support.
    3. Implement nested macro expansion.
    4. Add optimization features.

## 2025-01-09

- Fixed listing file generation for macros:
    - Added source line tracking for macro expansions
    - Updated instruction_sources tracking in program method
    - Fixed source information for jump instructions
    - Ensured proper line/column tracking for all instructions
    - Verified correct listing output format:
        - Address field (4 digits hex)
        - Machine code field (4 digits hex or "----" for labels)
        - Line:column information
        - Original source lines with comments
    - Tested with test_macros.asm:
        - Confirmed proper macro expansion
        - Verified source line correlation
        - Validated label handling
        - Checked jump resolution

- Improved macro handling:
    - Simplified macro body storage format
    - Removed Tree structure complexity
    - Maintained source line tracking through expansion
    - Added better error messages for:
        - Invalid macro structures
        - Missing source information
        - Malformed instructions
    - Preserved original source context in listings

- Test Coverage:
    - Verified macro expansion with test_macros.asm
    - Confirmed correct machine code generation:
        - Stack operations
        - ALU operations
        - Jump instructions
        - Label resolution
    - Validated listing file format
    - Checked symbol file generation
    - Tested error handling scenarios

- Next Steps:
    1. Add more complex macro test cases
    2. Consider adding macro parameter support
    3. Implement nested macro expansion
    4. Add optimization features

## 2025-01-08

- Implemented basic macro expansion:
    - Added macro definition and expansion in macro_processor.py
    - Macros are stored with their body instructions as Trees
    - Expansion returns raw instructions without re-parsing
    - Added error checking for:
        - Labels inside macros
        - Nested macro definitions
        - Recursive macro calls
        - Invalid instruction formats
    - Verified correct expansion with test_macros.asm
    - Confirmed correct hex output generation

- Fixed macro handling in assembler:
    - Updated macro_call method to use expand_macro directly
    - Removed string conversion and re-parsing of macro bodies
    - Integrated with existing instruction processing
    - Maintained source line tracking structure

- Known Issues:
    - --listing option not working:
        - instruction_sources not being populated for macro expansions
        - Need to track original source line for macro calls
        - Error: "not enough values to unpack (expected 3, got 2)"
    - Next steps:
        1. Debug instruction_sources population in program method
        2. Add source tracking for macro expansions
        3. Ensure macro calls preserve line/column information
        4. Update generate_listing to handle macro-expanded code

- Test Coverage:
    - Added test_macros.asm for basic macro testing
    - Verified against test_add_subroutine.asm equivalent
    - Confirmed correct machine code generation:
        - Stack operations working
        - Proper instruction expansion
        - Label resolution functioning

## 2025-01-07

- Refactored file generation in asm.py:
    - Created generate_output() method to handle hex output generation
    - Created generate_symbols() method to handle symbol file generation
    - Moved file generation logic from main() into J1Assembler class
    - Improved consistency across all file generation operations
    - Made code more maintainable and testable

- Enhanced listing file generation:
    - Added line and column numbers to listing output
    - Improved format consistency with explicit field spacing
    - Made multi-instruction line positions more visible
    - Added column information to help track instruction positions
    - Format: "Address  Machine Code  #:col  Source"
    - Example: "0000     802a          6:5    #$2A #10"
    - Helps identify source code formatting issues
    - Makes instruction positions in source clear

## 2025-01-06

- Working on `feature/forth-macros` branch.
    - Added Click library for CLI improvements:
        - Replaced argparse with Click for better CLI handling
        - Added `-o, --output` option for output file specification
        - Added `-d, --debug` flag for debug output
        - Set default output to aout.hex
        - Improved error handling with Click's error reporting
        - Updated setup.py to include Click dependency

    - Improved logging system:
        - Switched to Python's standard logging module
        - Removed redundant debug checks
        - Added proper logging configuration in conftest.py
        - Ensured consistent logging between CLI and tests
        - Added -J flag for debug output in pytest
        - Fixed logging configuration for test suite
        - Added force=True to prevent logging conflicts
        - Improved debug message formatting
        - Added comprehensive debug output for assembly process

    - added fimrware/test_* to test_assembler.py
    - Went through asm.py with debugger and cleaned up code

    - Added --symbols option for symbol file generation:
        - Added --symbols flag to Click CLI interface
        - Implemented .sym file generation alongside output
        - Symbol files contain sorted address-to-label mappings
            - Note: address is the word address, not byte address
        - Format: "ADDR LABEL" (e.g., "0000 main")
        - Uses same base name as output file with .sym extension
        - Added logging for symbol file generation
        - Documented symbol file format in feature_forth_macros.md

    - Added --listing option for assembly listing generation:
        - Added --listing flag to Click CLI interface
        - Implemented .lst file generation alongside output
        - Listing files show address, machine code, and source
        - Format includes:
            - Labels on their own lines before instructions
            - Machine code with original source line references
            - Full source line including comments
            - Support for multiple instructions per line
        - Uses same base name as output file with .lst extension
        - Added logging for listing file generation
        - Improved source line tracking for better listings

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
