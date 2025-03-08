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

Variables can be initialized at declaration time by appending one or more comma-separated values. The trailing comma indicates that the preceding number should be stored directly into memory at the current location. This syntax applies whether you are storing a single value or an array of values.

Examples:

```
VARIABLE counter 42,      // Initializes 'counter' with 42

// Defining an array using VARIABLE:
VARIABLE buffer 42, 43, 44, 45,  // 'buffer' will store these 4 values consecutively in memory
```

You can also use direct memory value initialization outside of variable declarations:

```
$10, $11, $12,       // Store hex values 10, 11, 12 sequentially at the current location
10, 20, 30,          // Store decimal values 10, 20, 30 sequentially
```

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

5. Direct memory values using the comma syntax simply store the provided value at the current memory location and advance the program counter.

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
5. Consider alignment for performance-critical data structures
6. When initializing memory directly, add comments describing data structures
7. Prefer the comma syntax for readability in data initialization
8. Be consistent with the use of the # prefix when pushing literals onto the stack