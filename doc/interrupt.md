# Understanding Interrupts in the J1 Processor

This document explains how to implement and use interrupts in the J1 processor architecture.

## Interrupt Basics

The J1 processor provides a simple interrupt mechanism that allows the system to respond to asynchronous events. When an interrupt occurs, the processor:

1. Completes the current instruction
2. Disables further interrupts
3. Jumps to the interrupt vector at address 0x0001 (word address)

## Setting Up Interrupts

### 1. Define the Interrupt Vector

The interrupt vector must be placed at word address 0x0001 (byte address 0x0002):

```forth
ORG #$0000
JMP start                // Boot vector

ORG #$0001               // word address 1, byte address 2
JMP irq_handler          // Interrupt vector
```

### 2. Create Memory Variables for Interrupt Handling

It's common to use memory variables to track interrupt counts or states:

```forth
// word address 2, byte address 4
macro: IRQ_COUNT0 ( -- ) #$0004 ;
macro: IRQ_COUNT1 ( -- ) #$0006 ;
```

### 3. Implement the Interrupt Handler

The interrupt handler should be as short as possible to minimize interrupt latency:

```forth
irq_handler:
    dint                    // Disable interrupts (already done by hardware, but good practice)
    
    // Handle the interrupt
    IRQ_COUNT0 @           // Fetch current count
    #1 +                   // Increment
    IRQ_COUNT0 !           // Store back
    
    // Additional processing if needed
    
    exit                   // Return from interrupt
```

### 4. Enable Interrupts

In your main program, enable interrupts using the `eint` instruction:

```forth
start:
    // Initialize hardware and variables
    #0 IRQ_COUNT0 !
    #0 IRQ_COUNT1 !
    
    eint                   // Enable interrupts
    
main_loop:
    // Main program logic
    JMP main_loop
```

## Memory Access in Interrupt Handlers

When accessing memory in interrupt handlers, use the correct fetch mechanism:

```forth
: @       ( addr -- x )
    #$4000 or  // Set bit 14 to mark as fetch address
    >r         // Push to return stack
    exit       // Trigger fetch sequence
    ;
```

## Interrupt Timing

The J1 processor typically generates interrupts based on a timer. The timing depends on your specific configuration:

- With a 24 MHz clock and a 2^16 cycle timer, interrupts occur every 2.73 ms
- This can be used to create precise timing for tasks like LED blinking

## Example: LED Toggle with Interrupts

This example toggles an LED approximately every 0.5 seconds using interrupts:

```forth
// Initialize variables
#0 IRQ_COUNT0 !
#0 IRQ_COUNT1 !

// Enable interrupts
eint

// Main loop
main_loop:
    IRQ_COUNT0 @ #183 > IF
        #0 IRQ_COUNT0 !
        led_toggle
    THEN
    JMP main_loop

// Interrupt handler
irq_handler:
    dint
    IRQ_COUNT0 @ #1 + IRQ_COUNT0 !
    exit
```

With an interrupt every 2.73 ms, this toggles the LED every 183 interrupts (approximately 0.5 seconds).

## Best Practices

1. **Keep Handlers Short**: Interrupt handlers should be as brief as possible
2. **Disable Interrupts**: Use `dint` to disable interrupts. (though hardware does this automatically for interrupt hanndler)
3. **Volatile Variables**: Remember that interrupt handlers can modify variables used by the main program
4. **Critical Sections**: Disable interrupts during critical sections of code with `dint`/`eint`
5. **Re-enable Interrupts**: The `exit` instruction at the end of the handler automatically re-enables interrupts

## Debugging Interrupts

When debugging interrupt-based code:

1. Add debug output to verify the handler is being called
2. Use counters to track interrupt frequency
3. Toggle LEDs or output to UART for visual/textual feedback
4. Verify timing calculations with oscilloscope measurements if possible

## Conclusion

Interrupts provide a powerful mechanism for handling asynchronous events in the J1 processor. By following these guidelines, you can implement reliable interrupt-driven applications that respond to timer events, external signals, or other asynchronous triggers.
