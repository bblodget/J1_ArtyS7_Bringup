# J1 Forth Standard Library

This directory contains the standard library for the J1 Forth processor. The library is organized into functional categories, each in its own subdirectory.

## Directory Structure

```
lib/
├── core/           # Core Forth words and stack manipulation
├── math/           # Mathematical operations
└── string/         # String manipulation (future)
```

## Library Organization

### Core Words (`core/`)
Contains fundamental Forth words and stack manipulation operations. These are the building blocks for more complex operations.

- `core_words.asm`: Basic stack manipulation and control flow
  - Stack operations (dup, drop, swap, over)
  - Basic control operations (noop)

### Math Operations (`math/`)
Mathematical operations built on core words.

- `math_words.asm`: Arithmetic and logical operations
  - Basic arithmetic (plus, minus)
  - Stack manipulation for math (2dup)
  - Comparisons
  - Bit operations
  - Shifts
  - Multiplication

### String Operations (`string/`)
*(Future expansion)*
Reserved for string manipulation operations.

## Usage

### Including Standard Library Files
Files from the standard library can be included using their relative paths from the library root:

```
include "core/core_words.asm"     // Include core words
include "math/math_words.asm"     // Include math operations
```

### Search Order
When resolving includes, the assembler searches in this order:
1. Current directory (where the source file is)
2. Explicitly specified include directories (via `-I` or `--include`)
3. Standard library directory

### Disabling Standard Library
The standard library can be disabled using the `--no-stdlib` flag:

```
j1asm source.asm --no-stdlib
```

## Contributing

When adding new words to the standard library:

1. Place files in appropriate subdirectories based on functionality
2. Document stack effects using standard notation: `( before -- after )`
3. Add comments explaining complex operations
4. Consider dependencies and include required files
5. Follow existing naming conventions

## File Naming Conventions

- Use descriptive names ending in `.asm`
- Use underscores to separate words in filenames
- Group related functionality into single files
- Consider using subdirectories for large collections of related words

## Documentation Format

Each word should be documented with:
- Stack effect comment
- Brief description
- Example usage (if not obvious)
- Implementation notes (if complex)

Example:
```
// Duplicates top two stack items
macro: 2dup ( a b -- a b a b )
    over    // Duplicate second item
    over    // Duplicate new top item
;
```