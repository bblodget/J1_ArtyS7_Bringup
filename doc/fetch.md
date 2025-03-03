# Understanding Memory Fetch in the J1 Processor

## Overview of the J1 Fetch Mechanism

Note: This is true for the J1-Universal-16kb-quickstore.v Verilog model.
It maybe different for other J1 models.

The J1 processor implements a unique memory fetch mechanism that uses bit 14 of the program counter (PC) to trigger a memory fetch operation. This document explains how this mechanism works and how to properly implement memory fetch operations in Forth code for the J1 processor.

## How Fetch Works in the J1 Processor

### The Bit 14 Mechanism

In the J1 processor, when bit 14 of the PC is set:

1. The processor recognizes this as a special instruction to fetch from memory
2. It clears bit 14 and uses the resulting address to fetch a value from memory
3. The fetched value is pushed onto the data stack
4. The processor then pops the next value from the return stack to continue execution

This mechanism is implemented in the processor's Verilog code:

```verilog
wire fetch = pc[14] & ~interrupt;  // Memory fetch data on pc[14] only valid if this is no interrupt entry.

// Stack gets the "fetch instruction", when fetch is asserted
// We are actually getting data here, not an instruction
casez ({fetch, insn[15:8]})
      ...
      9'b1_???_?????: st0N = insn;                                  // Memory fetch
      ...


// In the case statement for PC calculation:
casez ({notreboot, fetch, insn[15:13], insn[7], |st0})   // New address for PC
    7'b1_1_???_?_?,
    7'b1_0_011_1_?:   pcN = {1'b0, rst0[14:1], interrupt_enableN_return}; // Memory Fetch & ALU+exit: Return. Maybe reenable interrupts.
```

### Return Stack Management

The key to understanding the fetch mechanism is recognizing how the return stack is used:

1. The return stack is LIFO (Last In, First Out)
2. For a fetch operation, you need two addresses on the return stack:
   - The fetch address (with bit 14 set)
   - The return address (where to continue after the fetch)
3. These must be pushed in reverse order of how they'll be used

## Implementing Fetch in Forth

### Correct Implementation as a Subroutine

```forth
@:       
    // ( addr -- x )
    #$4000 or  // Set bit 14 to mark as fetch address
    >r         // Push to return stack
    exit       // Trigger fetch sequence
```

When this subroutine is called:

1. The `CALL @` instruction pushes the return address onto the return stack
2. The code ORs the address with 0x4000 (sets bit 14) and pushes it to the return stack
3. The `exit` instruction pops the fetch address (with bit 14 set) from the return stack
4. The processor performs the fetch and pushes the result onto the data stack
5. The processor then pops the next value from the return stack (the original return address)
6. Execution continues at the calling code with the fetched value on the data stack

### Why This Works

This implementation works because:

1. The return stack contains both addresses in the correct order
2. The `exit` instruction triggers the fetch mechanism
3. The processor correctly handles the return after the fetch

## Common Pitfalls

### Incorrect Implementation

A common mistake is to implement fetch without considering the return address:

```forth
macro: @       ( addr -- x )           
    #$4000 or >r exit ;  // INCORRECT!
```

This fails because:
- It doesn't account for the return address
- After the fetch, the processor has nowhere to return to

### Stack Order Issues

Another common issue is pushing the addresses in the wrong order:

```forth
macro: @       ( addr -- x )
    >r         // Push return address first (INCORRECT ORDER!)
    #$4000 or  // Set bit 14
    >r         // Push fetch address
    exit       // This will not work correctly
;
```

## Debugging Fetch Operations

When debugging fetch operations:

1. Check if the fetch address has bit 14 set (0x4000)
2. Verify that the return stack contains both addresses in the correct order
3. Confirm that the memory at the target address contains the expected value
4. Trace the execution flow to ensure the processor returns to the correct location

## Example: Complete Fetch Test

```forth
: test_fetch
    // Store a value in memory
    #8 #$0004 !
    
    // Emit 'A' to show we're before fetch
    #$41 emit
    
    // Fetch the value from memory
    #$0004 @
    
    // Emit 'B' to show fetch worked
    #$42 emit
    
    // Convert fetched value to ASCII and emit
    #$30 + emit
    ;
```

Expected output: `AB8`

## Conclusion

Understanding the J1 processor's fetch mechanism is essential for writing effective code. By properly managing the return stack and using bit 14 to trigger fetch operations, you can reliably access memory in your Forth programs.
