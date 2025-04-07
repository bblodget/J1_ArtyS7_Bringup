# Conditional Directives Implementation Plan

## Overview
This document outlines the step-by-step implementation plan for adding conditional assembly directives to the J1 assembler. Each step is designed to be small and testable, with pytest verification points to ensure we don't break existing functionality.

## Implementation Steps

### Step 1: Grammar Updates
- Add new tokens for conditional directives:
  - `.if`
  - `.else`
  - `.endif`
  - `.ifdef`
  - `.ifndef`
- Add grammar rules for conditional blocks
- Add grammar rules for equality comparison expressions
- Test point: Run `pytest tests/test_assembler.py` to verify grammar changes

### Step 2: Basic Directive Stub
- Add implementation for `if_directive` in `J1Assembler` class
    - Ade a new method `process_if_directive` in the `Directives` class
        - This method will be called by the if_directive method in the `J1Assembler` class
        - This method can be a stub for now.
- Ensure the stub doesn't break existing functionality
- Test point: Run `pytest tests/test_assembler.py` to verify no regressions

### Step 2.5: Conditional Block Handling Strategy
- Update grammar to use `directive_true_block` and `directive_false_block` instead of `block`
- Add state tracking in `Directives` class to handle conditional blocks
- In `process_if_directive`:
  - Extract condition parts (left_operand, right_operand)
  - Get the directive_true_block
  - Evaluate the condition
  - If true:
    - Process the block and allocate addresses
  - If false:
    - Skip the block
- This approach is similar to how macros handle block processing
- Test point: Run `pytest tests/test_assembler.py` to verify block handling

Example items value.  This is from the conditional.asm test case. Here is the items list
that is passed to process_if_directive:

0: Token('IF_DIRECTIVE', '.if')
1: Token('IDENT', 'TEST_CONST')
2: Token('EQUALS', '==')
3: Token('IDENT', '42')
4: Tree(Token('RULE', 'directive_true_block'),[instruction:]BYTE_CODE 1, instruction:JUMP CALL JMP, instruction:LABEL_REF 'wait_forever])
5: Token('ENDIF_DIRECTIVE', '.endif')

### Step 3: Implement the `process_if_directive` method

Implement the `process_if_directive` method in the `Directives` class

Example items value.  This is from the conditional.asm test case. Here are the Tokens in the items list:

0: Token('IF_DIRECTIVE', '.if')
1: Token('IDENT', 'TEST_CONST')
2: Token('EQUALS', '==')
3: Token('IDENT', '42')
4: Token('BLOCK', 'block')
5: Token('ENDIF_DIRECTIVE', '.endif')

We should update our items type hint in asm.py:if_directive and directives.py:process_if_directive to be a List of Tokens.




### Step 4: Expression Evaluation
- Add expression evaluation support to `Directives` class
- Support only equality comparison expressions (e.g., "a == b")
- Support constant substitution in expressions
- Test point: Run `pytest tests/test_assembler.py` to verify expression handling

### Step 5: Basic Conditional Processing
- Add conditional block state tracking to `J1Assembler`
- Implement basic `.if` directive processing
- Implement `.endif` directive processing
- Test point: Run `pytest tests/test_assembler.py` to verify basic conditional processing

### Step 6: Else Clause Support
- Add `.else` directive processing
- Handle nested conditionals
- Test point: Run `pytest tests/test_assembler.py` to verify else clause handling

### Step 7: Ifdef/Ifndef Support
- Add `.ifdef` directive processing
- Add `.ifndef` directive processing
- Test point: Run `pytest tests/test_assembler.py` to verify ifdef/ifndef handling

### Step 8: Integration Testing
- Add comprehensive test cases for all conditional directives
- Test nested conditionals
- Test equality comparison expressions
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
