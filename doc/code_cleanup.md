# J1Assembler Transformer Methods Organization

Based on the EBNF grammar, here's a hierarchical list of transformer methods in the J1Assembler class, organized from highest level (program) to lowest level (tokens):

## Top-level Structure
1. `program` (start symbol)
2. `statement`

## Directives
3. `org_directive`
4. `arch_flag_directive`
5. `define_directive`
6. `include_stmt`

## Code Elements
7. `instruction`
8. `label`
9. `memory_init_statement`
10. `macro_def` 
11. `call_expr`

## Control Structures
12. `if_then`
13. `if_else_then`
14. `loop_until`
15. `loop_while`
16. `do_loop`
17. `do_plus_loop`
18. `do_op`
19. `loop_op`
20. `plus_loop_op`

## Operations
21. [x] `jump_op`
22. [x] `address_of`
23. [x] `alu_op`
24. [x] `basic_alu`

## Modifiers
25. [x] `modifiers`
26. [x] `modifier_list`
27. [x] `modifier`
28. [x] `stack_effect`
29. [x] `stack_delta`
30. [x] `data_stack_delta`
31. [x] `return_stack_delta`

## Low-level Elements
32. [x] `raw_number`
33. [x] `labelref`

## Missing Implementations
There are several grammar rules that don't appear to have transformer methods:
- `statement_type`
- `control_structure`
- `block`
- `block_item`
- `macro_body`

## Recommended Approach for Cleanup

For each transformer method:

1. Define a clear input type (what items should contain)
2. Define a clear return type
3. Add type hints to improve code readability and maintainability
4. Handle edge cases like None values consistently
5. Add docstrings explaining the method's purpose, expected input, and return value

Your current implementation has some methods returning either a single item or a list of items, which creates complexity. Standardizing these to consistently return a specific type would make the code more maintainable.

Would you like me to start with refactoring a specific transformer method as an example?