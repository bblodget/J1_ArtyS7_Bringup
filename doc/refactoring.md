# J1 Assembler Refactoring Plan

The current asm.py file is growing large and would benefit from being split into more focused modules. This document outlines a plan to reorganize the codebase for better maintainability.

## Proposed Module Structure

### 1. Control Structure Handlers (`control_structures.py`)
Handles all control flow constructs:
- IF THEN
- IF ELSE THEN
- BEGIN UNTIL
- BEGIN WHILE REPEAT
- DO LOOP

```python
class ControlStructureHandler:
    def if_then(self, items): ...
    def if_else_then(self, items): ...
    def loop_until(self, items): ...
    def loop_while(self, items): ...
    def do_loop(self, items): ...
```

### 2. Macro Processing (`macro_processor.py`)
Manages macro definitions and expansions:
```python
class MacroProcessor:
    def process_macro_def(self, items): ...
    def expand_macro(self, name, token): ...
```

### 3. Address Space Management (`address_space.py`)
Handles memory layout and address allocation:
```python
class AddressSpace:
    def set_org(self, address): ...
    def advance(self, size=1): ...
    def get_word_address(self): ...
```

### 4. Instruction Handlers (`instruction_handlers.py`)
Processes basic instructions:
```python
class InstructionHandler:
    def number(self, items): ...
    def basic_alu(self, items): ...
    def alu_op(self, items): ...
```

### 5. Main Assembler (`assembler.py`)
Core assembler functionality:
```python
class J1Assembler(ControlStructureHandler, InstructionHandler):
    def __init__(self): ...
    def transform(self, tree): ...
    def generate_output(self, output_file): ...
```

### 6. Constants and Types (`constants.py`)
Shared constants and type definitions:
```python
ALU_OPS = {...}
STACK_EFFECTS = {...}
JUMP_OPS = {...}
```

### 7. Entry Point (`__main__.py`)
Command-line interface:
```python
def main(): ...
```

## Implementation Strategy

### Phase 1: Preparation
1. Create new module files
2. Set up proper imports
3. Update build configuration if needed

### Phase 2: Code Migration
1. Move code piece by piece to new modules
2. Update imports and references
3. Ensure tests pass after each move

### Phase 3: Testing
1. Add unit tests for new modules
2. Verify existing integration tests
3. Add new integration tests if needed

### Phase 4: Documentation
1. Update module docstrings
2. Update README.md
3. Add module-specific documentation

### Phase 5: Cleanup
1. Remove redundant code
2. Standardize interfaces
3. Final testing pass

## Benefits

1. **Maintainability**
   - Smaller, focused modules
   - Clear separation of concerns
   - Easier to understand and modify

2. **Testability**
   - Isolated components
   - Easier to mock dependencies
   - Better test coverage

3. **Extensibility**
   - Clear extension points
   - Easier to add new features
   - Better organized for future growth

4. **Documentation**
   - Better organized documentation
   - Clearer component responsibilities
   - Easier to maintain

## Future Considerations

1. Consider adding a plugin system for:
   - Custom instructions
   - New control structures
   - Output formats

2. Potential additional modules:
   - Error handling
   - Optimization passes
   - Debug information generation

## Timeline

This refactoring should be implemented after:
1. Basic DO LOOP implementation is complete and tested
2. All current features are stable
3. Test coverage is adequate

The refactoring itself should be done incrementally to maintain a working system throughout the process.