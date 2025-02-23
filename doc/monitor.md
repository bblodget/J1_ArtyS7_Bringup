# J1 Monitor System

The J1 Monitor System provides a live coding environment that allows uploading and executing user programs while maintaining system control through a resident monitor program.

## Memory Layout

The system uses a 4KB (2048 16-bit words) block RAM with the following layout:

| Address Range (hex) | Size (words) | Purpose |
|--------------------|--------------|----------|
| 0x000 - 0x001 | 2 | Boot and Interrupt Vectors |
| 0x002 - 0x003 | 2 | Interrupt Handler Entry |
| 0x004 - 0x3FF | 1022 | User Program Space (~2KB) |
| 0x400 - 0x7FF | 1024 | Monitor Program Space (2KB) |

## System Operation

### Boot Sequence
The system starts execution at address 0x000, which contains a jump to the monitor initialization routine. The monitor initializes the system state, enables interrupts, and either waits for user input or jumps to a previously loaded user program.

### Thread Management
The system uses timer-based interrupts to switch between the monitor and user programs:
1. Timer generates periodic interrupts
2. Interrupt handler saves user program context
3. Monitor program checks for commands/input
4. If no monitor tasks are pending, user context is restored and execution returns

### Serial Protocol
The monitor uses a simple protocol to distinguish between commands and data:

| Sequence | Purpose |
|----------|---------|
| 0xFF | Command Escape Character |
| 0xFF 01 | Start Code Upload |
| 0xFF 02 | Start Program Execution |
| 0xFF 03 | Stop Program Execution |
| Other | Normal Data |

### Context Switching
The interrupt handler manages context switching between user and monitor programs:
- Saves user program state (data stack, return stack, top-of-stack)
- Switches to monitor execution
- On return, restores user state if returning to user program

### Memory Protection
The monitor space (0x400-0x7FF) is protected from user program writes to ensure system stability. User programs are restricted to accessing memory below 0x400.

## Monitor Commands
The monitor provides the following basic commands:
- Upload: Load user program into memory
- Run: Start user program execution
- Stop: Halt user program execution
- Status: Display system state

## Implementation Notes
- Uses timer-based interrupts for thread switching
- Interrupt vector at 0x002 points to thread switching code
- Monitor maintains separate stack space from user program
- Serial communication handled through existing UART interface

## Initial Implementation Idea

```forth
// J1 Monitor System
// Provides live coding environment with monitor and user program threads

ORG #$0000
JMP monitor_init        // Boot vector jumps to monitor initialization

ORG #$0002
JMP irq_handler        // Interrupt vector

include "core/j1_base_macros.asm"      
include "core/j1_extended_macros.asm"   
include "io/terminal_io.asm"

// Monitor system variables (high memory)
// These are at fixed locations in high memory
ORG #$7F0              // Reserve last 16 words for system variables
: user_dsp     #0 ;    // User data stack pointer save
: user_rsp     #0 ;    // User return stack pointer save
: user_pc      #0 ;    // User program counter save
: user_st0     #0 ;    // User top of stack save

// Monitor initialization
: monitor_init ( -- )
    // Initialize system
    #monitor_prompt user_pc !    // Set initial user PC to prompt
    eint                        // Enable interrupts
    monitor_prompt              // Start monitor prompt
    ;

// Interrupt handler - saves user context and switches to monitor
: irq_handler ( -- )
    // Save user context
    status user_dsp !          // Save data stack pointer
    rstatus user_rsp !         // Save return stack pointer
    T user_st0 !               // Save top of stack
    
    // Switch to monitor context
    monitor_check_input        // Check for monitor commands
    
    // Restore user context and return if no monitor action needed
    user_st0 @ T->N           // Restore top of stack
    user_pc @ JMP             // Return to user code
    ;

// Monitor command check
: monitor_check_input ( -- )
    // Check if UART has data
    #$2000 io@ #1 and IF      // Check UART status
        key                    // Get character
        #$FF = IF             // Check for command escape
            handle_command     // Process command
        ELSE
            drop              // Discard normal character during interrupt
        THEN
    THEN
    ;

// Monitor prompt
: monitor_prompt ( -- )
    s" J1 Monitor> " type     // Print prompt
    key                       // Wait for command
    handle_command            // Process command
    monitor_prompt            // Loop
    ;

// Command handler
: handle_command ( c -- )
    dup #$01 = IF            // Upload command
        drop
        do_upload
    ELSE dup #$02 = IF       // Run command
        drop
        do_run
    ELSE dup #$03 = IF       // Stop command
        drop
        do_stop
    ELSE                     // Unknown command
        drop
    THEN THEN THEN
    ;

// Upload handler - placeholder
: do_upload ( -- )
    s" Upload mode" type
    #$0A emit               // Newline
    ;

// Run handler - placeholder
: do_run ( -- )
    s" Running user program" type
    #$0A emit               // Newline
    ;

// Stop handler - placeholder
: do_stop ( -- )
    s" Stopped user program" type
    #$0A emit               // Newline
    ;
```