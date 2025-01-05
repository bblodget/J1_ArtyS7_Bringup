# Forth Macros Feature Branch

## Overview
The `feature/forth-macros` branch aims to simplify the J1 assembler by separating core functionality from high-level Forth-like operations. High-level words will be implemented using a macro system with Forth-like syntax.

## Goals

1. **Simplify Core Assembler**
   - Remove high-level word implementations from core assembler
   - Focus on fundamental J1 instructions only
   - Maintain clean separation between core instructions and macros

2. **Implement Forth-like Macro System**
   - Support `macro:` definitions with stack effect comments
   - Add `include` directive for macro libraries
   - Preserve compatibility with existing assembly syntax
   - Support nested includes with cycle detection

3. **Add Optimization Features**
   - Support constant folding through `foldable:` directive
   - Enable inline expansion with `inline:` directive
   - Maintain simulation stack during assembly
   - Optimize compile-time constants

## Implementation Plan

### Phase 1: Core Cleanup
1. Remove high-level word definitions from `instructionset_16kb_dualport.py`
2. Update grammar in `j1.lark` to focus on core instructions
3. Simplify `asm.py` to handle only fundamental operations

### Phase 2: Macro System
1. Add `include` directive to grammar
2. Implement macro definition parsing
   - Support `macro:` syntax
   - Parse stack effect comments
   - Handle trailing semicolons
3. Create macro expansion system
   - First pass: collect macro definitions
   - Second pass: expand macros
   - Third pass: resolve labels and generate code

### Phase 3: Optimization Features
1. Implement constant folding
   - Add `foldable:` directive
   - Create compile-time operation emulator
   - Add simulation stack
2. Add inlining support
   - Implement `inline:` directive
   - Support `INLINE` for existing subroutines

## File Structure

```
j1tools/
├── j1tools/
│   └── assembler/
│       ├── asm.py              # Core assembler (simplified)
│       ├── j1.lark            # Updated grammar
│       ├── macro_processor.py # New: Macro handling
│       └── optimizer.py       # New: Constant folding/inlining
└── lib/
    └── forth/
        ├── core_words.forth   # Standard high-level words
        ├── math.forth         # Math operations
        └── string.forth       # String handling
```

## Example Usage

```forth
; my_program.asm
include "lib/forth/core_words.forth"

; Define custom macro
macro: triple ( n -- n*3 ) DUP DUP + + ;

; Use macros in code
main:
    #5 triple     ; Expands to DUP DUP + +
    #3 +          ; Uses + from core_words
    RET
```

## Testing Strategy

1. **Unit Tests**
   - Macro expansion
   - Include directive processing
   - Constant folding
   - Inline expansion

2. **Integration Tests**
   - Complete programs using macros
   - Nested includes
   - Complex optimizations

3. **Regression Tests**
   - Ensure existing assembly code still works
   - Verify binary compatibility

## Migration Path

1. Create macro versions of all existing high-level words
2. Update example code to use macro system
3. Provide documentation for converting existing code
4. Keep backward compatibility during transition

## Future Enhancements

1. **Macro Libraries**
   - Standard library of common Forth words
   - User-definable library paths
   - Version control for macro libraries

2. **Advanced Optimizations**
   - Pattern-based optimizations
   - Dead code elimination
   - Stack effect analysis

3. **Development Tools**
   - Macro expansion viewer
   - Stack effect checker
   - Optimization report generator

## Command-Line Interface Enhancements

### Overview
The assembler's command-line interface will be enhanced to support the macro system, control optimizations, and generate additional output files for debugging and development.

### Basic Usage
```bash
j1asm source.asm              # Outputs to aout.hex
j1asm -o program.hex source.asm
```

### Output Options
```bash
-o, --output FILE            # Specify output file (default: aout.hex)
--symbols                    # Generate symbol file (.sym)
--listing                    # Generate listing file (.lst)
```

Example symbol file (program.sym):
```
0000 main
0001 square
0002 multiply
...
```

Example listing file (program.lst):
```
Address  Machine Code  Source
0000     6011         main:    DUP        ; Expanded from macro
0001     6203                  +          ; Expanded from macro
0002     6088                  RET
```

### Include Path Options
```bash
-I, --include DIR           # Add directory to include search path
```

Example:
```bash
j1asm -I lib -I include source.asm
```

Search order:
1. Current directory
2. Directories specified by -I (in order)
3. System-wide macro library path

### Optimization Controls
```bash
--opt-level N              # Set optimization level (0-3)
--no-fold                 # Disable constant folding
--no-inline               # Disable inlining
```

Optimization levels:
- 0: No optimizations
- 1: Basic constant folding
- 2: Default - constant folding and simple inlining
- 3: Aggressive optimizations (future use)

### Debug Options
```bash
-d, --debug               # Enable debug output
--preprocess, -E         # Output preprocessed assembly
--dump-ir                # Dump intermediate representation
```

Example IR dump (program.ir):
```python
# Internal representation after parsing and macro expansion
{
    'sections': {
        '.code': {
            'address': 0x0000,
            'instructions': [
                {
                    'type': 'label',
                    'name': 'main',
                    'address': 0x0000
                },
                {
                    'type': 'literal',
                    'value': 5,
                    'address': 0x0000,
                    'source_line': 4,
                    'original': '#5'
                },
                {
                    'type': 'alu',
                    'operation': 'T',
                    'modifiers': ['T->N', 'd+1'],
                    'address': 0x0001,
                    'source_line': 4,
                    'expanded_from': 'DUP'
                },
                # ... more instructions ...
            ]
        }
    },
    'macros': {
        'triple': {
            'stack_effect': '( n -- n*3 )',
            'body': ['DUP', 'DUP', '+', '+'],
            'defined_at': 'lib/forth/math.forth:12'
        }
    },
    'symbols': {
        'main': 0x0000,
        'square': 0x0010
    }
}
```

The `--dump-ir` option:
- Shows the program's internal structure
- Useful for debugging the assembler itself
- Helps understand how macros are processed
- Shows all metadata collected during assembly
- Primarily intended for assembler development

The `-E/--preprocess` option:
- Performs all include file processing
- Expands all macros
- Resolves all optimizations
- Outputs clean, low-level assembly
- Preserves comments showing macro origins
- Useful for debugging and verification

### Future CLI Enhancements

1. **Macro Control**
   - `--trace-macros`: Show macro expansion process
   - `--macro-path`: Override default macro library path
   - `--preprocess-only`: Stop after macro expansion

2. **Output Formats**
   - `--format=hex|bin|mif`: Select output format
   - `--annotate`: Add source comments to output
   - `--map`: Generate memory map file

3. **Development Tools**
   - `--stack-check`: Enable stack effect verification
   - `--word-usage`: Report word usage statistics
   - `--cross-reference`: Generate cross-reference file