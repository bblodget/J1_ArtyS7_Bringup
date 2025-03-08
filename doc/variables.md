# J1 Assembler Memory and Variable Support

This document describes the variable, array, and constant support in the J1 assembler. These features allow for more structured memory management and initialization that follows Forth conventions while being adapted for assembly language use.

## Numeric Literals

In the J1 Assembler, prefixing a number with a `#` tells the assembler that this literal should be pushed onto the stack. For example:

```
#42          // Push decimal value 42 onto the stack
#$2A         // Push hexadecimal value 2A (42 decimal) onto the stack
```

When defining a variable with inline initialization (using the comma syntax), you do not use the `#` because these values are stored directly into memory rather than pushed onto the stack:

```
VARIABLE timer 100,    // Store 100 directly in memory
```

When defining a constant, you also omit the `#` in the definition, but the constant expands to code that pushes its value onto the stack when used:

```
CONSTANT MAX_SIZE 100  // Defines MAX_SIZE to push 100 onto the stack when used
```

In summary:
- Use `#` when you want to push a literal value onto the stack in code
- Omit `#` when storing values directly into memory (with comma syntax)
- Omit `#` in constant definitions, though they will push their value when used

This distinction helps clarify the difference between stack operations and memory operations.

## Character and String Literals

### Character Literals

For character literals, use the syntax `#'c'` where the character is enclosed in single quotes and preceded by the `#` prefix (indicating you want to push the value onto the stack):

```
#'A'        // Pushes 65 (ASCII value of 'A') onto the stack
#'!'        // Pushes 33 (ASCII value of '!') onto the stack
```

Character literals can be used anywhere numeric literals are accepted. For example:

```
counter #'X' !       // Store ASCII value of 'X' (88) into counter
#'A' emit            // Output the character 'A' to the console
```

### String Literals

For strings, use the `STRING` directive which defines a counted string in memory (where the first byte contains the length):

```
STRING greeting "Hello, world!"
```

This:
1. Stores the length of the string (13) as the first byte
2. Stores the characters "Hello, world!" in the subsequent bytes (one character per byte, 8-bits each)
3. Defines a macro named `greeting` that pushes the address of the first byte (the count byte) onto the stack

This approach follows standard Forth counted string conventions, making it compatible with traditional Forth string handling words.

**Important Note:** Characters in strings are stored as bytes (8-bits), not as full words (16-bits). This means that string operations use byte-addressing rather than word-addressing when manipulating individual characters. However, the address returned by the string name is still a word address that points to the length byte.

### String Access and Manipulation

Since strings are just stored in memory as a sequence of bytes, you can access and manipulate them using byte-oriented operations:

```
greeting                // Pushes the address of the string (pointing to count byte)
greeting c@             // Fetches the length byte (13 for "Hello, world!")
greeting 1+ c@          // Fetches the first character ('H') as a byte
greeting 1+ 5 + c@      // Fetches the 6th character (',' in this case)
greeting 1+ 5 + #'X' c! // Replaces the 6th character with 'X'
```

Note the use of `c@` and `c!` for byte access (character fetch and store) rather than the word-oriented `@` and `!` operations.

For string printing, you might define words like:
```
: type ( addr -- )  // Print a counted string
  dup c@ >r         // Get the length byte and save it
  1+               // Skip past the count byte
  r> 0 do          // Loop through each character
    dup i + c@     // Fetch the character byte
    emit           // Output it
  loop
  drop ;
```

### Implementation Details

Under the hood, the string directive is implemented as follows:

`STRING name "text"` expands to:
```
macro: name ( -- addr ) #$MEMORY_ADDR endmacro
// Store the length byte, followed by each character as individual bytes
13c, 'H'c, 'e'c, 'l'c, 'l'c, 'o'c, ... // For example, with "Hello, world!"
```

The characters are stored as 8-bit values (bytes) to maintain compatibility with standard Forth string conventions and to optimize memory usage. Note that the STRING directive automatically calculates the length of the provided text string.

### Direct Memory Initialization with Characters

Characters can also be used with the comma syntax for direct memory initialization. For a counted string:

```
13c, 'H'c, 'e'c, 'l'c, 'l'c, 'o'c, ','c, ' 'c, 'w'c, 'o'c, 'r'c, 'l'c, 'd'c, '!'c,  // Counted string "Hello, world!"
```

Where the first byte (13) indicates the string length.

## Variable Declaration

Variables reserve one or more words of memory and define a name that pushes the variable's address when used. When declared without any initialization values, a variable defaults to 0. You can also initialize a variable (or an array) by providing one or more comma-separated initialization values. In the case of multiple values, the variable stores an array of words in consecutive memory locations, and the variable's name refers to the base address of that array.

Examples:

```
VARIABLE counter           // Declare a variable 'counter' (initialized to 0 by default)
VARIABLE timer 100,        // Declare a variable 'timer' initialized to 100
VARIABLE buffer 42, 43, 44, 45,  // Declare 'buffer' as an array with 4 initialized values
```

Usage:

```
counter @           // Fetch value from 'counter'
counter #42 !        // Store 42 into 'counter'

buffer 2 + @        // Fetch the third value from 'buffer' (i.e., 44)
buffer 3 + #99 !     // Store 99 into the fourth element of 'buffer'
```

## Constants

Constants define a name that pushes a fixed value when used.

```
CONSTANT MAX_SIZE 100  // Define 'MAX_SIZE' to push 100 onto the stack
```

Usage:

```
MAX_SIZE            // Pushes 100 onto the stack
```

## Memory Initialization

### Direct Initialization

Variables can be initialized at declaration time by appending one or more comma-separated values. The trailing comma (`,`) indicates that the preceding number should be stored directly into memory as a 16-bit word. This syntax applies whether you are storing a single value or an array of values.

Examples:

```
VARIABLE counter 42,      // Initializes 'counter' with 42 (as a 16-bit word)
VARIABLE char_h 'h',      // Store ASCII value of 'h' (104) as a 16-bit word in memory

// Defining an array using VARIABLE:
VARIABLE buffer 42, 43, 44, 45,  // 'buffer' will store these 4 values as words consecutively in memory
```

You can also use direct memory value initialization outside of variable declarations:

```
$10, $11, $12,       // Store hex values 10, 11, 12 sequentially as 16-bit words
10, 20, 30,          // Store decimal values 10, 20, 30 sequentially as 16-bit words
```

### Byte-Level Memory Operations

For byte-level memory operations, use the `c,` syntax (analogous to Forth's `C,` word). This stores a single byte (8-bits) in memory instead of a full word:

```
$30c, $31c, $32c, $33c,  // Store four bytes in memory (using 8-bits each)
'H'c, 'e'c, 'l'c, 'l'c, 'o'c, 0c,  // Store "Hello" as bytes followed by a null terminator
```

This is particularly useful for:
- Character data when you don't need full 16-bit words
- Counted strings and C-style strings
- Byte arrays where memory efficiency is important

You can use byte-level operations with VARIABLE declarations as well:

```
VARIABLE ascii_str 'H'c, 'i'c, '!'c, 0c,  // Stores "Hi!" as bytes
```

### Endianness

The J1 processor uses little-endian byte order. When a 16-bit word (e.g., $ABCD) is stored in memory:
- The least significant byte ($CD) is stored at the lower address
- The most significant byte ($AB) is stored at the higher address

This affects how bytes are accessed when using word-oriented and byte-oriented operations on the same memory locations.

## Label Addressing

In the J1 Assembler, a bare label (for example, a subroutine name) is by default translated to a call instruction (i.e., it compiles as `CALL label`). However, there are cases when you might want to push the address of a label onto the stack rather than calling it.

To do this, you simply prefix the label with a single quote (often called the tick operator). For example:

```
: my_subroutine
  ...   // subroutine code
;

'my_subroutine   // Pushes the address of 'my_subroutine' onto the stack
```

This approach mirrors traditional Forth usage, where the tick operator is used to obtain a word's execution token (address), and provides a clear distinction between calling a subroutine and retrieving its address.

### Modifying Table Values

Label addressing is especially useful when working with tables. For example, suppose you define a table as follows:

```
: my_table
  $01, $02, $03,     // Table with three values
```

Here, the label `my_table` corresponds to the base address of the table. To modify a specific element in the table, you can use the tick operator to obtain the base address, perform an arithmetic offset to target the desired element, and then use the store operator (`!`) to write a new value. For instance, to change the second value in the table to `$FF`, you would write:

```
'my_table 1 + #$FF !
```

In this example, `'my_table` pushes the base address of the table onto the stack, `1 +` computes the address of the second element (since addresses are word-indexed), and `#$FF !` stores the new value `$FF` into that memory location.

## Reserving Memory Blocks (RESERVE Keyword)

Sometimes you may need to reserve a block of memory without initializing it inline. For this purpose, we introduce the `RESERVE` keyword. The syntax is as follows:

```
RESERVE label size
```

This reserves `size` words of memory and defines a macro named `label` that pushes the base address of the reserved block onto the stack. This is particularly useful for creating large arrays or data structures that will be initialized later or are intended to be modified at runtime.

### Example

```
RESERVE buffer 100   // Reserves 100 words for the array 'buffer'
```

You can access and modify elements within the reserved block by using arithmetic with the label. For instance, to fetch the value of the 43rd word (index 42) and then update it:

```
buffer 42 + @       // Fetch the value at buffer[42]
buffer 42 + #$FF !  // Store $FF into buffer[42]
```

Note that unlike labels defined with `:`, variables and reserved blocks automatically push their address when referenced, so you don't need to use the tick operator with them.

## Implementation Details

Under the hood, these directives are implemented as follows:

1. `VARIABLE name` expands to a macro that returns the current memory address:
   ```
   macro: name ( -- addr ) #$MEMORY_ADDR endmacro
   ```
   If no initialization values are provided, a 0 is stored by default:
   ```
   0,   // Store 0 at that location using the comma syntax
   ```

2. `VARIABLE name` with initialization values expands to:
   ```
   macro: name ( -- addr ) #$MEMORY_ADDR endmacro
   value1, value2, ...   // Store each value at consecutive memory locations
   ```
   For example, the declaration:
   ```
   VARIABLE buffer 42, 43, 44, 45,
   ```
   causes 42, 43, 44, and 45 to be stored in consecutive memory cells, and the macro `buffer` returns the address of the first cell.

3. `CONSTANT name value` expands to:
   ```
   macro: name ( -- value ) #value endmacro
   ```

4. `RESERVE name size` expands to:
   ```
   macro: name ( -- addr ) #$MEMORY_ADDR endmacro
   ORG #$MEMORY_ADDR+size  // Reserve space for size words
   ```

5. Direct memory values using the comma syntax:
   - `value,` stores a full word (16-bits) at the current memory location and advances the program counter by 1 word
   - `value c,` stores a single byte (8-bits) at the current memory location and advances the program counter by 1 byte

6. `STRING name "text"` expands to:
   ```
   macro: name ( -- addr ) #$MEMORY_ADDR endmacro
   lengthc, 'c1'c, 'c2'c, 'c3'c, ... // Where each character is stored as a byte
   ```

## Comparison with Traditional Forth

This implementation provides a syntax that is familiar to Forth programmers while being adapted for an assembly context:

| Traditional Forth                            | J1 Assembler                         |
|----------------------------------------------|--------------------------------------|
| `VARIABLE x`                                 | `VARIABLE x`                         |
| `CREATE arr 10 CELLS ALLOT`                  | `RESERVE arr 10`                     |
| `10 CONSTANT MAX`                            | `CONSTANT MAX 10`                    |
| `CREATE tbl 1 , 2 , 3 ,`                     | `: tbl 1, 2, 3,`                     |

The key difference is that in this implementation, variable names automatically expand to push their address onto the stack, whereas in traditional Forth, they are defined as words that push addresses when executed.

## Best Practices

1. Group related variable declarations together
2. Use constants for magic numbers
3. Initialize variables and arrays with meaningful defaults
4. Ensure arrays are sized appropriately to avoid wasting memory
5. Consider alignment for performance-critical data structures:
   - Align word-oriented data on word boundaries when possible
   - Be mindful of byte/word mixing which can lead to misaligned accesses
6. When initializing memory directly, add comments describing data structures
7. Prefer the comma syntax for readability in data initialization
8. Be consistent with the use of the # prefix when pushing literals onto the stack
9. Use `c,` for byte storage and `,` for word storage consistently
10. When processing strings, remember to use byte-oriented operations (`c@`, `c!`) rather than word operations