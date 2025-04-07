# Conditional Directives Implementation Plan

## Overview
This document outlines the step-by-step implementation plan for adding conditional assembly directives to the J1 assembler. Each step is designed to be small and testable, with pytest verification points to ensure we don't break existing functionality.

## Implementation Steps

### Step 1: Grammar Updates ✅
- Added new tokens for conditional directives:
  - `.if`
  - `.else`
  - `.endif`
  - `.ifdef`
  - `.ifndef`
- Added grammar rules for conditional blocks
- Added grammar rules for equality comparison expressions
- Test point: Run `pytest tests/test_assembler.py` to verify grammar changes

### Step 2: Basic Directive Stub ✅
- Added implementation for `if_directive` in `J1Assembler` class
- Added `process_if_directive` method in `Directives` class
- The stub doesn't break existing functionality
- Test point: Run `pytest tests/test_assembler.py` to verify no regressions

### Step 2.5: Conditional Block Handling Strategy ✅
- Updated grammar to use `directive_true_block` and `directive_false_block` instead of `block`
- No state tracking needed in `Directives` class - blocks are processed statelessly
- In `process_if_directive`:
  - Extract condition parts (left_operand, right_operand)
  - Get the directive_true_block
  - Evaluate the condition
  - If true:
    - Process the block and allocate addresses
  - If false:
    - Skip the block and undo address space advances
- This approach is similar to how macros handle block processing
- Test point: Run `pytest tests/test_assembler.py` to verify block handling

Example items value from conditional.asm test case:
```python
0: Token('IF_DIRECTIVE', '.if')
1: Token('IDENT', 'TEST_CONST')
2: Token('EQUALS', '==')
3: Token('IDENT', '42')
4: Tree(Token('RULE', 'directive_true_block'),[instruction:]BYTE_CODE 1, instruction:JUMP CALL JMP, instruction:LABEL_REF 'wait_forever])
5: Token('ENDIF_DIRECTIVE', '.endif')
```

### Step 3: Implement the `process_if_directive` method
- Update type hints to handle both Tokens and Trees:
  ```python
  def process_if_directive(self, items: List[Union[Token, Tree]]) -> Optional[List[InstructionMetadata]]
  ```
- Handle different types of right operands:
  - IDENT (constant reference)
  - STACK_DECIMAL (decimal literal)
  - STACK_HEX (hex literal)
- Implement proper error handling for:
  - Undefined constants
  - Invalid operand types
  - Invalid block contents
- Test point: Add test cases for different operand types and error conditions

### Step 4: Expression Evaluation
- We already have `evaluate_expression` in `Directives` class
- Add specific test cases for conditional expressions
- Ensure proper error handling for undefined constants
- Test point: Run `pytest tests/test_assembler.py` to verify expression handling

### Step 5: Basic Conditional Processing
- No need for state tracking in `J1Assembler`
- Implement basic `.if` directive processing
- Implement `.endif` directive processing
- Handle address space management for skipped blocks
- Test point: Run `pytest tests/test_assembler.py` to verify basic conditional processing

### Step 6: Else Clause Support
- Add `.else` directive processing
- Handle nested conditionals
- Ensure proper address space management for both true and false blocks
- Test point: Run `pytest tests/test_assembler.py` to verify else clause handling

### Step 7: Ifdef/Ifndef Support
- Leverage existing `constant_exists` method
- Handle the case where a constant is defined but has a value of 0
- Ensure proper error messages for undefined constants
- Test point: Run `pytest tests/test_assembler.py` to verify ifdef/ifndef handling

### Step 8: Integration Testing
- Add comprehensive test cases for:
  - Nested conditionals
  - Complex expressions
  - Address space management
  - Error conditions
  - Edge cases with constants
- Test point: Run `pytest tests/test_assembler.py` to verify full functionality

## Test Strategy
Each step will be verified using pytest with the following approach:
1. Run existing tests to ensure no regressions
2. Add new tests for the current step's functionality
3. Verify all tests pass before moving to next step

## Error Handling
Each step will include appropriate error handling:
- Invalid expressions
- Missing endif
- Nested conditional errors
- Undefined constants
- Invalid syntax
- Invalid operand types
- Invalid block contents

## Documentation
After each step:
1. Update relevant documentation
2. Add examples
3. Document any limitations or edge cases

## Rollback Plan
If any step fails:
1. Revert changes for that step
2. Analyze failure
3. Fix issues
4. Retry step
5. Only proceed when all tests pass
