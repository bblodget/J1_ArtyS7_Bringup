# Call Expression Feature

## Overview

Traditionally, subroutine calls in our J1 assembler required the explicit use of the `CALL` keyword. With this update, you can now invoke subroutines simply by using a bare identifier—aligning the assembler more closely with Forth-like calling conventions.

## How It Works

When the assembler processes an identifier as part of a program:
- **Macro Check:**  
  It first checks if the identifier is associated with a macro definition.
- **Subroutine Call:**  
  If the identifier is _not_ a macro, it is interpreted as a subroutine call. Internally, the identifier is converted into a `CALL` instruction that references the subroutine label.

This dual functionality is achieved by:
- Renaming the parsing rule to `call_expr` in our grammar.
- Updating the assembler transformer to generate a `CALL` instruction for bare identifiers that aren’t defined as macros.

## Benefits

- **Forth-Like Style:** Allows subroutine calls using bare identifiers (e.g., `mySubroutine`), providing a more natural Forth-like coding style.
- **Backward Compatibility:** Existing code that uses explicit `CALL` statements continues to work without any modification.
- **Flexible Usage:** Developers can mix both calling styles in the same project as needed.

## Syntax and Usage

### Using Bare Identifiers

With this feature, you can now call subroutines by simply writing the subroutine name. For example, consider the following code snippet:

```asm
ORG #$0000
JMP start

include "io/terminal_io.asm"

start:
    key // Read the character (treated as "CALL key")
    emit // Echo it back (treated as "CALL emit")
    #$0A emit // Send newline (ASCII 0x0A): becomes "CALL emit"
```

Here:
- `key` and `emit` are interpreted as subroutine calls if they are not defined as macros.
- This style reduces verbosity and mirrors the way Forth words are typically invoked.

### Explicit CALL

The traditional explicit call style remains fully supported:

```asm
CALL key
CALL emit
```

## Example

Suppose you have a subroutine defined as follows:

```asm
mySub:
    // Subroutine implementation
```

You can now call this subroutine using either style:

```asm
mySub // Bare identifier call
CALL mySub // Explicit CALL
```

## Key Points

- **Macro Check:**  
  The assembler first checks if the identifier is associated with a macro definition.
- **Subroutine Call:**  
  If the identifier is not a macro, it is interpreted as a subroutine call.

  ## Conclusion

  This enhancement makes the J1 assembler more flexible and developer-friendly by supporting both macro expansion and subroutine call generation through a single, unified `call_expr` rule. Enjoy a cleaner, more concise assembly coding experience that better reflects Forth-inspired design!
