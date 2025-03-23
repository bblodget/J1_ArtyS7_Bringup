# J1 Assembler Development Tasks

## Completed Features
- [x] Initial Grammar and Syntax
  - [x] ALU operations, stack modifiers, stack deltas
  - [x] Instruction encoding (ALU, stack, return stack, data stack bits)
  - [x] Support for literals, jumps, and labels
  - [x] Basic error handling with line numbers
  - [x] Complex identifier support (Forth-style operators)
    - [x] Number-operator combinations (2*, 2/)
    - [x] Special char prefix/suffix (>r, r@)
    - [x] Special char infix (dup>r)
    - [x] Pure operator sequences (+, -, etc)

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

- [x] Assembler Improvements
  - [x] Warning for unresolved jumps in included files
  - [x] Error for undefined labels in main file
  - [x] Added main file tracking
  - [x] Preserved test coverage
  - [x] Basic UART write test
  - [x] Status register read
  - [x] Fixed stack manipulation in UART status checking
  - [x] Identified simulator UART status always returns 0xF
  - [x] Echo test (TX -> RX loopback)
  - [x] Subroutine Call Syntax
    - [x] Allow direct subroutine names as CALL targets
    - [x] Update grammar to recognize bare identifiers as calls
    - [x] Maintain backward compatibility with explicit CALL
    - [x] Add documentation for both calling styles
  - [x] Entry Point Handling
    - [x] Remove temporary JMP start from library files
  - [x] Address and Memory Management
    - [x] Enhanced Listing Output
      - [x] Show both byte and word addresses
      - [x] Add address column headers (BYTE/WORD)
      - [x] Align address columns
    - [x] Origin Directive Support
      - [x] Add 'ORG' keyword to grammar
      - [ ] Implement address space management
      - [ ] Handle non-contiguous code blocks
      - [ ] Add collision detection
      - [ ] Update listing generation for ORG blocks
      - [ ] Optimize address range tracking (in address_space.py)
        - [ ] Merge adjacent ranges
        - [ ] Consider range objects for better management
        - [ ] Add performance testing with large programs
  - [x] Added comparison macros
    - [x] Greater than (>)
    - [x] Unsigned greater than (u>)
  - [x] Fix subroutine return instruction
    - [x] Make ; generate T[RET,r-1] instead of RET
    - [x] Update grammar to handle bare ; correctly
    - [x] Test coverage for return stack handling
  - [ ] Include file improvements
    - [ ] Add include guard detection
    - [ ] Track already included files
    - [ ] Prevent duplicate includes
    - [ ] Test with circular includes
  - [x] Architecture Flag Support
    - [x] Document architecture variants (fetch_type, alu_ops)
    - [x] Create framework for configuration options
    - [x] Document assembly directives for flags

## Current Development Focus

### Control Structures
- [x] IF THEN
- [x] IF ELSE THEN
- [x] BEGIN WHILE REPEAT
- [x] BEGIN UNTIL
- [x] DO LOOP Control Structure
  - [x] Grammar support for DO, LOOP, +LOOP
  - [x] Loop index words (i, j, k) as macros
  - [x] Instruction generation
  - [x] Label management
  - [x] Stack effect validation
  - [x] Warning system for index words outside loops
  - [x] Test coverage
    - [x] Basic DO LOOP
    - [x] Nested loops
    - [x] Loop indices (i, j, k)
    - [x] Index warning system
    - [x] +LOOP with different increments
    - [x] Negative increment support
  - [ ] Support for LEAVE

- [ ] BEGIN AGAIN Control Structure
  - [ ] Grammar support
  - [ ] Instruction generation
  - [ ] Label management
  - [ ] Test coverage
  - [ ] Documentation
  - [ ] Stack effect validation

### Hardware Testing
- [x] UART Testing
  - [x] Hardware timing verification
  - [x] Multi-byte transmission test
  - [x] Add realistic UART status simulation
  - [x] Implement key? in simulator
  - [x] Test with actual hardware
- [x] Interrupt System
  - [x] Interrupt Handler
    - [x] Test ticks overflow interrupt
    - [x] Implement basic interrupt service routine
    - [x] Add interrupt vector table
    - [x] Document interrupt handling
  - [ ] Advanced interrupt features
    - [ ] Multiple interrupt sources
    - [ ] Priority handling
    - [ ] Nested interrupts

### Standard Library Development
- [ ] Core Word Library
  - [x] Document all J1 ALU operations
  - [x] Create macros for all single-instruction operations
    - [x] Update grammar to support operator symbols in macro names
  - [ ] Add stack effect documentation
  - [ ] Add operation descriptions
  - [ ] Test coverage for all operations
    - [x] Basic stack operations
    - [x] ALU operations
    - [x] Comparison operations
    - [x] Shift operations
    - [ ] Return stack operations
    - [x] I/O operations
    - [ ] Status operations

### CLI Enhancements
- [x] Test Organization
  - [x] Move test files from firmware/ to j1tools/tests/test_files/
  - [x] Create organized category directories
  - [x] Update test_assembler.py to use parameterized tests
  - [x] Verify all tests passing in new structure
- [ ] Optimization Controls
  - [ ] `--opt-level N`
  - [ ] `--no-fold`, `--no-inline`
- [ ] Debug Options
  - [ ] `--preprocess`
  - [ ] `--dump-ir`
  - [ ] `--trace-macros`

### Macro System Enhancements
- [ ] Improve listing file
  - [x] Show macro chain in comments. // (macro: 2dup.over) 
  - [ ] Provide filename somehow. Give each file a number for reference?
- [ ] Macro Parameters
  - [ ] Parameter syntax definition
  - [ ] Parameter substitution
  - [ ] Test coverage

### High-Level Assembly Support
- [ ] Case insensitive keywords
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
- [x] Memory Fetch Operations
  - [x] Implement @ fetch as subroutine
  - [x] Test with actual hardware
  - [x] Document fetch behavior

### Hardware Features
- [ ] Parameter Register File
  - [ ] >P(n) instruction
  - [ ] Parameter scope management
  - [ ] Assembler support
- [x] LED Control
  - [x] Basic on/off functionality
  - [x] Toggle with timing control
  - [x] Integration with interrupt system

### Architecture Support
- [ ] J1 Architecture Variants
  - [x] Document architecture flags
  - [ ] Implement architecture flag directives
  - [ ] Add configuration constants
  - [ ] Support conditional assembly
  - [ ] Test with different configurations

### Code Organization
- [ ] Code Refactoring
  - [ ] Split asm.py into focused modules (see doc/refactoring.md)
  - [ ] Create new module structure
    - [ ] control_structures.py
    - [ ] macro_processor.py
    - [ ] instruction_handlers.py
    - [ ] assembler.py
    - [ ] constants.py
    - [ ] __main__.py
  - [ ] Migrate code incrementally
  - [ ] Update tests
  - [ ] Update documentation

## Future Enhancements
- [ ] Forth-like Syntax
  - [x] Function definitions (`: name ... ;`)
  - [ ] Stack effect validation
  - [ ] Optimization directives
- [ ] Binary Output Support
- [ ] Disassembler
- [ ] Advanced Memory Features
  - [ ] Memory initialization
  - [ ] Section placement controls
- [ ] Improved J1 architecture support diffs
  - [ ] Add compile flag for architecture

## Project Management
- [ ] Licensing
  - [ ] Add SwapForth license to 3rd party licenses
  - [ ] Create LICENSE file
  - [ ] Add copyright notices to source files

## Bug Fixes
- [x] Issue with control structures in subroutines
  - [x] I think we can make subroutines just syntax sugar for a label
- [ ] Need to check for include files more than once

## Notes
- Focus on BEGIN AGAIN implementation next
- Consider parameter register file implementation
- Plan for disassembler development
- Focus on implementing architecture flag directives next
- Consider adding more examples for interrupt handling
- Document memory fetch patterns for different architectures

## Next
 - [ ] Make sure we have all the functionality from refactor/code_cleanup branch
   - [ ] Add architecture flag support (.arch_flag directive)
   - [ ] Add define support (.define directive)
   - [ ] Update grammar and assembler implementation
 - [ ] Need profile stuff
 - [ ] Need all the tests
 - [ ] Need to clean up the docstrings in asm.py
